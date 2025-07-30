// Prevents additional console window on Windows in release, DO NOT REMOVE!!
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use tauri::{Manager, State};
use serde::{Deserialize, Serialize};
use std::sync::Mutex;
use std::fs;
use std::path::PathBuf;
use chrono::{DateTime, Utc, Local};

// 数据结构定义
#[derive(Debug, Serialize, Deserialize, Clone)]
struct UserSettings {
    reminder_interval: u32,
    exercise_duration: u32,
    repetitions: u32,
    enable_sound: bool,
    enable_notifications: bool,
    theme: String,
    working_hours_start: String,
    working_hours_end: String,
    working_hours_enabled: bool,
}

impl Default for UserSettings {
    fn default() -> Self {
        Self {
            reminder_interval: 30,
            exercise_duration: 60,
            repetitions: 10,
            enable_sound: true,
            enable_notifications: true,
            theme: "light".to_string(),
            working_hours_start: "09:00".to_string(),
            working_hours_end: "18:00".to_string(),
            working_hours_enabled: true,
        }
    }
}

#[derive(Debug, Serialize, Deserialize, Clone)]
struct ExerciseStats {
    today_count: u32,
    week_count: u32,
    month_count: u32,
    total_count: u32,
    streak_days: u32,
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
    data_dir: PathBuf,
}

impl AppState {
    fn new(data_dir: PathBuf) -> Self {
        Self {
            settings: Mutex::new(UserSettings::default()),
            stats: Mutex::new(ExerciseStats::default()),
            data_dir,
        }
    }

    fn load_data(&self) -> Result<(), Box<dyn std::error::Error>> {
        // 加载设置
        let settings_path = self.data_dir.join("settings.json");
        if settings_path.exists() {
            let settings_data = fs::read_to_string(&settings_path)?;
            let settings: UserSettings = serde_json::from_str(&settings_data)?;
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
    *state.settings.lock().unwrap() = settings;

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
    next_reminder: Option<String>,
    interval: u32,
}

#[tauri::command]
fn get_reminder_status(state: State<AppState>) -> Result<ApiResponse<ReminderStatus>, String> {
    let settings = state.settings.lock().unwrap();

    let status = ReminderStatus {
        enabled: settings.enable_notifications,
        next_reminder: None, // 这里可以计算下次提醒时间
        interval: settings.reminder_interval,
    };

    Ok(ApiResponse {
        success: true,
        message: "提醒状态获取成功".to_string(),
        data: Some(status),
    })
}

#[tauri::command]
fn toggle_reminder(state: State<AppState>) -> Result<ApiResponse<bool>, String> {
    let mut settings = state.settings.lock().unwrap();
    settings.enable_notifications = !settings.enable_notifications;
    let enabled = settings.enable_notifications;
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

fn main() {
    tauri::Builder::default()
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

            // 创建应用状态
            let app_state = AppState::new(app_data_dir);

            // 加载数据
            if let Err(e) = app_state.load_data() {
                println!("Warning: Failed to load data: {}", e);
            }

            // 设置应用状态
            app.manage(app_state);

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
            toggle_reminder
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
