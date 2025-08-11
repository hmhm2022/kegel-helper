@echo off
echo ========================================
echo Git 推送脚本
echo ========================================

echo 1. 设置 Git 代理...
git config --global http.proxy http://127.0.0.1:10809
git config --global https.proxy http://127.0.0.1:10809
echo 代理设置完成

echo.
echo 2. 检查 Git 状态...
git status --porcelain
echo.

echo 3. 添加所有变更...
git add .
echo 文件添加完成

echo.
echo 4. 提交变更...
git commit -m "feat: 重构项目架构并修复提醒功能 - 移除Python后端，完全迁移到Tauri架构 - 修复提醒功能问题 - 清理项目结构"
echo 提交完成

echo.
echo 5. 推送到 GitHub...
git push origin main
echo 推送完成

echo.
echo ========================================
echo 所有操作完成！
echo ========================================
pause
