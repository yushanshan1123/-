# 在线 Demo 部署步骤（Render 最快版）

目标：拿到一个可访问的在线 URL，提供 `/runtime` HTTP 接口用于演示。

## 1. 准备 GitHub 仓库
1) 你在 GitHub 新建一个仓库（例如：`xinbi-contract-calm-demo`）
2) 把我打包的代码解压后上传到仓库（或我后面帮你补齐 `git init` 推送）

仓库里要包含：
- `http_runtime_server.py`
- `http_runtime_entry_mock.py`（以及其依赖）
- `services/`
- `render.yaml`

## 2. Render 部署
1) 打开 https://render.com/ 登录
2) New → **Blueprint**（推荐，因为我们提供了 `render.yaml`）
3) 选择你的 GitHub 仓库
4) Render 会自动识别并创建一个 Web Service

默认启动命令：
- `python3 http_runtime_server.py`

Render 会自动注入 `PORT` 环境变量，服务将监听 `0.0.0.0:$PORT`。

## 3. 验证 Demo
部署成功后，你会拿到类似：
- `https://<service>.onrender.com`

接口：
- `POST https://<service>.onrender.com/runtime`

请求示例（body 结构取决于 runtime action 设计）：
```json
{
  "action": "snapshot",
  "payload": {"pair": "RIVERUSDT"}
}
```

## 4. 用于参赛提交
- 在线 Demo：填写 Render 的 URL
- GitHub 仓库：填写你的 repo URL
- 演示视频：录屏展示：token-check → snapshot/risk-check → 输出模板
