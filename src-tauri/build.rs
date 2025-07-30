fn main() {
    // 启用tauri_build来正确处理图标资源
    tauri_build::build();

    // 设置Windows子系统
    println!("cargo:rustc-link-arg=/SUBSYSTEM:WINDOWS");
}
