// Prevents additional console window on Windows in release, DO NOT REMOVE!!
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use tauri::{Manager, State, SystemTray, SystemTrayMenu, SystemTrayMenuItem, CustomMenuItem, SystemTrayEvent, WindowEvent};
use serde::{Deserialize, Serialize};
use std::sync::Mutex;
use std::fs;
use std::path::PathBuf;
use chrono::{Local, Timelike};
use std::time::{Duration, Instant};

// 数据结构定义
#[derive(Debug, Serialize, Deserialize, Clone)]
struct WorkingHours {
    start: String,
    end: String,
    enabled: bool,
}

impl Default for WorkingHours {
    fn default() -> Self {
        Self {
            start: "09:00".to_string(),
            end: "18:00".to_string(),
            enabled: true,
        }
    }
}

#[derive(Debug, Serialize, Deserialize, Clone)]
struct UserSettings {
    #[serde(rename = "reminderInterval")]
    reminder_interval: u32,
    #[serde(rename = "exerciseDuration")]
    exercise_duration: u32,
    repetitions: u32,
    #[serde(rename = "enableSound")]
    enable_sound: bool,
    #[serde(rename = "enableNotifications")]
    enable_notifications: bool,
    theme: String,
    #[serde(rename = "workingHours")]
    working_hours: WorkingHours,
    #[serde(skip_serializing_if = "Option::is_none")]
    last_reminder_time: Option<String>, // 添加最后提醒时间，但不序列化到前端
}

impl Default for UserSettings {
    fn default() -> Self {
        Self {
            reminder_interval: 30,
            exercise_duration: 5, // 修改为与前端一致的默认值
            repetitions: 10,
            enable_sound: true,
            enable_notifications: true,
            theme: "light".to_string(),
            working_hours: WorkingHours::default(),
            last_reminder_time: None,
        }
    }
}

#[derive(Debug, Serialize, Deserialize, Clone)]
struct ExerciseStats {
    #[serde(rename = "todayCount")]
    today_count: u32,
    #[serde(rename = "weekCount")]
    week_count: u32,
    #[serde(rename = "monthCount")]
    month_count: u32,
    #[serde(rename = "totalCount")]
    total_count: u32,
    #[serde(rename = "streakDays")]
    streak_days: u32,
    #[serde(rename = "lastExerciseTime")]
    last_exercise_time: Option<String>,
}

impl Default for ExerciseStats {
    fn default() -> Self {
        Self {
            today_count: 0,
            week_count: 0,
            month_count: 0,
            total_count: 0,
            streak_days: 0,
            last_exercise_time: None,
        }
    }
}

#[derive(Debug, Serialize, Deserialize)]
struct ApiResponse<T> {
    success: bool,
    message: String,
    data: Option<T>,
}

// 应用状态
struct AppState {
    settings: Mutex<UserSettings>,
    stats: Mutex<ExerciseStats>,
    reminder_timer: Mutex<ReminderTimer>,
    data_dir: PathBuf,
}

impl AppState {
    fn new(data_dir: PathBuf) -> Self {
        Self {
            settings: Mutex::new(UserSettings::default()),
            stats: Mutex::new(ExerciseStats::default()),
            reminder_timer: Mutex::new(ReminderTimer {
                enabled: false,
                interval_minutes: 30,
                last_reminder: None,
                last_reminder_time: None,
                working_hours_enabled: true,
                working_hours_start: "09:00".to_string(),
                working_hours_end: "18:00".to_string(),
            }),
            data_dir,
        }
    }

    fn load_data(&self) -> Result<(), Box<dyn std::error::Error>> {
        // 加载设置
        let settings_path = self.data_dir.join("settings.json");
        if settings_path.exists() {
            let settings_data = fs::read_to_string(&settings_path)?;
            let settings: UserSettings = serde_json::from_str(&settings_data)?;

            // 同步timer状态
            {
                let mut timer = self.reminder_timer.lock().unwrap();
                timer.enabled = settings.enable_notifications;
                timer.interval_minutes = settings.reminder_interval;
                timer.working_hours_enabled = settings.working_hours.enabled;
                timer.working_hours_start = settings.working_hours.start.clone();
                timer.working_hours_end = settings.working_hours.end.clone();
                timer.last_reminder_time = settings.last_reminder_time.clone();

                // 如果有保存的提醒时间，转换为Instant
                if let Some(time_str) = &settings.last_reminder_time {
                    if let Ok(saved_time) = chrono::DateTime::parse_from_rfc3339(time_str) {
                        let now = chrono::Local::now();
                        let duration_since = now.signed_duration_since(saved_time);
                        if let Ok(std_duration) = duration_since.to_std() {
                            timer.last_reminder = Some(Instant::now() - std_duration);
                        }
                    }
                }
            }

            *self.settings.lock().unwrap() = settings;
        }

        // 加载统计数据
        let stats_path = self.data_dir.join("stats.json");
        if stats_path.exists() {
            let stats_data = fs::read_to_string(&stats_path)?;
            let stats: ExerciseStats = serde_json::from_str(&stats_data)?;
            *self.stats.lock().unwrap() = stats;
        }

        Ok(())
    }

    fn save_settings(&self) -> Result<(), Box<dyn std::error::Error>> {
        let settings = self.settings.lock().unwrap().clone();
        let settings_data = serde_json::to_string_pretty(&settings)?;
        let settings_path = self.data_dir.join("settings.json");
        fs::write(&settings_path, settings_data)?;
        Ok(())
    }

    fn save_stats(&self) -> Result<(), Box<dyn std::error::Error>> {
        let stats = self.stats.lock().unwrap().clone();
        let stats_data = serde_json::to_string_pretty(&stats)?;
        let stats_path = self.data_dir.join("stats.json");
        fs::write(&stats_path, stats_data)?;
        Ok(())
    }
}

// Tauri命令函数
#[tauri::command]
fn get_settings(state: State<AppState>) -> Result<ApiResponse<UserSettings>, String> {
    let settings = state.settings.lock().unwrap().clone();
    Ok(ApiResponse {
        success: true,
        message: "设置获取成功".to_string(),
        data: Some(settings),
    })
}

#[tauri::command]
fn update_settings(settings: UserSettings, state: State<AppState>) -> Result<ApiResponse<()>, String> {
    // 更新设置
    *state.settings.lock().unwrap() = settings.clone();

    // 同步更新定时器配置
    {
        let mut timer = state.reminder_timer.lock().unwrap();
        if timer.enabled {
            // 如果定时器正在运行，更新其配置
            timer.interval_minutes = settings.reminder_interval;
            timer.working_hours_enabled = settings.working_hours.enabled;
            timer.working_hours_start = settings.working_hours.start.clone();
            timer.working_hours_end = settings.working_hours.end.clone();

            // 重置last_reminder，让新的间隔立即生效
            timer.last_reminder = None;
        }
    }

    if let Err(e) = state.save_settings() {
        return Err(format!("保存设置失败: {}", e));
    }

    Ok(ApiResponse {
        success: true,
        message: "设置更新成功".to_string(),
        data: None,
    })
}

#[tauri::command]
fn get_stats(state: State<AppState>) -> Result<ApiResponse<ExerciseStats>, String> {
    let stats = state.stats.lock().unwrap().clone();
    Ok(ApiResponse {
        success: true,
        message: "统计数据获取成功".to_string(),
        data: Some(stats),
    })
}

#[tauri::command]
fn start_exercise(state: State<AppState>) -> Result<ApiResponse<String>, String> {
    let now = Local::now().to_rfc3339();

    Ok(ApiResponse {
        success: true,
        message: "运动开始".to_string(),
        data: Some(now),
    })
}

#[tauri::command]
fn complete_exercise(state: State<AppState>) -> Result<ApiResponse<()>, String> {
    let mut stats = state.stats.lock().unwrap();

    // 更新统计数据
    stats.today_count += 1;
    stats.total_count += 1;
    stats.last_exercise_time = Some(Local::now().to_rfc3339());

    // 这里可以添加更复杂的统计逻辑，比如周统计、月统计等

    drop(stats); // 释放锁

    if let Err(e) = state.save_stats() {
        return Err(format!("保存统计数据失败: {}", e));
    }

    Ok(ApiResponse {
        success: true,
        message: "运动完成".to_string(),
        data: None,
    })
}

#[derive(Debug, Serialize, Deserialize)]
struct ReminderStatus {
    enabled: bool,
    #[serde(rename = "nextReminder")]
    next_reminder: Option<String>,
    interval: u32,
}

// 定时器状态
#[derive(Debug)]
struct ReminderTimer {
    enabled: bool,
    interval_minutes: u32,
    last_reminder: Option<Instant>,
    last_reminder_time: Option<String>, // 添加可序列化的时间字符串
    working_hours_enabled: bool,
    working_hours_start: String,
    working_hours_end: String,
}

#[tauri::command]
fn get_reminder_status(state: State<AppState>) -> Result<ApiResponse<ReminderStatus>, String> {
    let _settings = state.settings.lock().unwrap();
    let timer = state.reminder_timer.lock().unwrap();

    let next_reminder = if timer.enabled {
        if let Some(last) = timer.last_reminder {
            // 有上次提醒记录，计算下次提醒时间
            let next_time = last + Duration::from_secs(timer.interval_minutes as u64 * 60);
            let now = Instant::now();

            if next_time > now {
                // 计算下次提醒的绝对时间
                let duration_until_next = next_time.duration_since(now);
                let next_absolute = Local::now() + chrono::Duration::from_std(duration_until_next).unwrap_or_default();
                Some(next_absolute.to_rfc3339())
            } else {
                Some(Local::now().to_rfc3339()) // 应该立即提醒
            }
        } else {
            // 如果启用了但还没有上次提醒记录，下次提醒就是现在开始计算
            let next_absolute = Local::now() + chrono::Duration::minutes(timer.interval_minutes as i64);
            Some(next_absolute.to_rfc3339())
        }
    } else {
        None
    };

    let status = ReminderStatus {
        enabled: timer.enabled,
        next_reminder,
        interval: timer.interval_minutes,
    };

    Ok(ApiResponse {
        success: true,
        message: "提醒状态获取成功".to_string(),
        data: Some(status),
    })
}

#[tauri::command]
fn toggle_reminder(state: State<AppState>) -> Result<ApiResponse<bool>, String> {
    let mut timer = state.reminder_timer.lock().unwrap();
    let mut settings = state.settings.lock().unwrap();

    timer.enabled = !timer.enabled;
    settings.enable_notifications = timer.enabled;

    if timer.enabled {
        // 启动定时器，设置last_reminder为None，让check_reminder函数处理首次启动
        timer.interval_minutes = settings.reminder_interval;
        timer.working_hours_enabled = settings.working_hours.enabled;
        timer.working_hours_start = settings.working_hours.start.clone();
        timer.working_hours_end = settings.working_hours.end.clone();
        timer.last_reminder = None; // 重置为None，让check_reminder处理
    } else {
        // 停止定时器
        timer.last_reminder = None;
    }

    let enabled = timer.enabled;
    drop(timer);
    drop(settings);

    if let Err(e) = state.save_settings() {
        return Err(format!("保存设置失败: {}", e));
    }

    Ok(ApiResponse {
        success: true,
        message: format!("提醒已{}", if enabled { "开启" } else { "关闭" }),
        data: Some(enabled),
    })
}

// 检查是否需要发送提醒
fn check_reminder(state: &AppState, app_handle: &tauri::AppHandle) {
    let mut timer = state.reminder_timer.lock().unwrap();

    if !timer.enabled {
        return;
    }

    let now = Instant::now();
    let interval_duration = Duration::from_secs(timer.interval_minutes as u64 * 60);

    // 如果是首次启动（没有last_reminder），或者已经到了提醒时间
    let should_remind = if let Some(last_reminder) = timer.last_reminder {
        now.duration_since(last_reminder) >= interval_duration
    } else {
        // 首次启动，立即设置last_reminder为当前时间减去间隔，这样下次检查就会提醒
        timer.last_reminder = Some(now - interval_duration);
        true
    };

    if should_remind {
        // 检查是否在工作时间内
        if timer.working_hours_enabled {
            let current_time = Local::now();
            let current_hour_minute = format!("{:02}:{:02}", current_time.hour(), current_time.minute());

            if current_hour_minute < timer.working_hours_start || current_hour_minute > timer.working_hours_end {
                return; // 不在工作时间内，跳过提醒
            }
        }

        // 发送提醒
        send_reminder_notification(app_handle);

        // 更新最后提醒时间
        timer.last_reminder = Some(now);
        timer.last_reminder_time = Some(Local::now().to_rfc3339());

        // 释放timer锁
        drop(timer);

        // 更新设置中的last_reminder_time并保存
        {
            let mut settings = state.settings.lock().unwrap();
            settings.last_reminder_time = Some(Local::now().to_rfc3339());
            drop(settings);

            // 保存设置到文件
            if let Err(e) = state.save_settings() {
                println!("保存提醒时间失败: {}", e);
            }
        }
    }
}

// 发送提醒通知
fn send_reminder_notification(app_handle: &tauri::AppHandle) {
    use tauri::api::notification::Notification;

    // 发送系统通知
    match Notification::new(&app_handle.config().tauri.bundle.identifier)
        .title("kegel-helper")
        .body("该做提肛运动了！保持健康从现在开始 💪")
        .show() {
        Ok(_) => println!("提醒通知发送成功"),
        Err(e) => println!("提醒通知发送失败: {}", e),
    }

    // 如果窗口被隐藏，可以选择显示窗口
    if let Some(window) = app_handle.get_window("main") {
        match window.set_focus() {
            Ok(_) => println!("窗口焦点设置成功"),
            Err(e) => println!("窗口焦点设置失败: {}", e),
        }
    }
}

#[tauri::command]
fn check_and_send_reminder(state: State<AppState>, app_handle: tauri::AppHandle) -> Result<ApiResponse<bool>, String> {
    check_reminder(&state, &app_handle);
    Ok(ApiResponse {
        success: true,
        message: "提醒检查完成".to_string(),
        data: Some(true),
    })
}

fn main() {
    // 创建系统托盘菜单
    let show = CustomMenuItem::new("show".to_string(), "显示窗口");
    let hide = CustomMenuItem::new("hide".to_string(), "隐藏窗口");
    let quit = CustomMenuItem::new("quit".to_string(), "退出");
    let tray_menu = SystemTrayMenu::new()
        .add_item(show)
        .add_item(hide)
        .add_native_item(SystemTrayMenuItem::Separator)
        .add_item(quit);

    // 创建系统托盘
    let system_tray = SystemTray::new().with_menu(tray_menu);

    tauri::Builder::default()
        .system_tray(system_tray)
        .on_system_tray_event(|app, event| match event {
            SystemTrayEvent::LeftClick {
                position: _,
                size: _,
                ..
            } => {
                // 左键点击托盘图标显示窗口
                if let Some(window) = app.get_window("main") {
                    let _ = window.show();
                    let _ = window.set_focus();
                }
            }
            SystemTrayEvent::MenuItemClick { id, .. } => {
                match id.as_str() {
                    "show" => {
                        if let Some(window) = app.get_window("main") {
                            let _ = window.show();
                            let _ = window.set_focus();
                        }
                    }
                    "hide" => {
                        if let Some(window) = app.get_window("main") {
                            let _ = window.hide();
                        }
                    }
                    "quit" => {
                        std::process::exit(0);
                    }
                    _ => {}
                }
            }
            _ => {}
        })
        .on_window_event(|event| match event.event() {
            WindowEvent::CloseRequested { api, .. } => {
                // 阻止窗口关闭，改为隐藏到系统托盘
                event.window().hide().unwrap();
                api.prevent_close();
            }
            _ => {}
        })
        .setup(|app| {
            // 获取应用数据目录
            let app_data_dir = app.path_resolver()
                .app_data_dir()
                .expect("Failed to get app data directory");

            // 确保数据目录存在
            if !app_data_dir.exists() {
                fs::create_dir_all(&app_data_dir)
                    .expect("Failed to create app data directory");
            }

            // 打印数据目录位置
            println!("应用数据目录: {:?}", app_data_dir);
            println!("设置文件位置: {:?}", app_data_dir.join("settings.json"));
            println!("统计文件位置: {:?}", app_data_dir.join("stats.json"));

            // 创建应用状态
            let app_state = AppState::new(app_data_dir);

            // 加载数据
            if let Err(e) = app_state.load_data() {
                println!("Warning: Failed to load data: {}", e);
            }

            // 设置应用状态
            app.manage(app_state);

            // 启动定时检查提醒的后台任务
            let app_handle = app.handle();
            std::thread::spawn(move || {
                loop {
                    std::thread::sleep(Duration::from_secs(60)); // 每分钟检查一次
                    if let Some(state) = app_handle.try_state::<AppState>() {
                        check_reminder(&state, &app_handle);
                    }
                }
            });

            println!("Application initialized successfully");
            Ok(())
        })
        .invoke_handler(tauri::generate_handler![
            get_settings,
            update_settings,
            get_stats,
            start_exercise,
            complete_exercise,
            get_reminder_status,
            toggle_reminder,
            check_and_send_reminder
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
