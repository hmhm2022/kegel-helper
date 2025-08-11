@echo off
cd /d "%~dp0"
git add .
git commit -m "feat: 重构项目架构并修复提醒功能"
git push origin main
echo 完成！
pause
