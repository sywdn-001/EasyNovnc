# EasyNovnc
--------------------------
### 引言
###### EasyNovnc 是一个旨在简化 **noVNC** 和 **websockify** 部署与管理的自动化工具。它提供了一个直观的交互式命令行界面（CLI），让用户能够轻松配置 VNC 代理、管理访问令牌以及一键启动服务。
###### 本程序由**13岁初一学生**开发，若有不足，欢迎各位大佬多多指教，**`多发发issues`**
--------------------------
![LogoBanner.png](https://raw.githubusercontent.com/sywdn-001/EasyNovnc/refs/heads/main/LogoBanner.png)

## ✨ 特性

- **一键部署**：自动检测并安装必要的组件（如 websockify）。
- **交互式管理**：基于 `rich` 库构建的精美 CLI 界面，操作简单。
- **令牌系统**：通过 Token 机制管理多个远程桌面连接，增强安全性。
- **自动检测**：自动获取本地网络 IP，生成访问链接。
- **页面加密**：支持为 noVNC 访问页面设置密码保护。
- **多终端支持**：支持在独立控制台中启动服务，方便监控日志。

## 🚀 快速开始

### 前提条件

- **操作系统**：Windows 或者WindowsServer(必须Windows)

- **Python**：3.9+

- **依赖库**：

  ```bash
  pip install rich
  ```

### 安装与运行(仅限于Windows)

1. 克隆或下载本仓库到本地。

2. 在项目根目录下打开终端（PowerShell 或 CMD）。

3. 运行主配置程序：

   ```bash
   python configure_novnc.py
   ```

4. 或者打开Powershell一键安装:

​    `powershell -NoProfile -ExecutionPolicy Bypass -Command "irm https://gh.llkk.cc/https://github.com/sywdn-001/EasyNovnc/raw/refs/heads/main/build.ps1 | iex"`

​    失败的话多试几次



## 🛠️ 功能说明

在交互式界面中，你可以执行以下操作：

1.  **安装 websockify**：如果系统中未检测到 websockify，可以使用此选项进行一键安装。
2.  **新增 Token**：添加一个新的 VNC 映射。你需要提供目标主机的 IP 和端口（默认 5900）。程序会自动生成一个高强度的 Token。
3.  **删除 Token**：管理现有的连接映射。
4.  **启动服务器**：启动 websockify 代理服务。启动后，你可以通过生成的链接访问远程桌面。
5.  **刷新检测**：重新扫描项目环境和配置文件。
6.  **查看连接网址**：显示当前可用的访问链接。
7.  **设置查看页面密码**：为 `index.html` 设置简单的访问权限校验。

## 📂 项目结构

- `configure_novnc.py`: 项目主入口，交互式配置工具。
- `modules/`: 核心逻辑模块，包含检测、下载、网络、Token 管理等功能。
- `noVNC-1.6.0/`: 内置的 noVNC 静态资源。
- `websockify-0.13.0/`: 内置的 websockify 源码。
- `token.conf`: 存储 Token 与后端 VNC 地址的映射关系。

## 📝 注意事项

- 请确保防火墙允许 6080 端口（默认）的入站连接。
- 建议在受信任的网络环境中使用，或配合更高强度的安全措施。

## 🔌 第三方组件

----------------------------------

<table>
  <tr>
    <td width="120" align="center">
      <img src="https://kimi-web-img.moonshot.cn/img/static.celiss.com/372271f023d5de27c9c01f7201d1791b609fb0e9" width="80" alt="NoVNC Logo">
    </td>
    <td>
      <h3>noVNC</h3>
      <p>
        <a href="https://github.com/novnc/noVNC"><img src="https://img.shields.io/badge/GitHub-novnc%2FnoVNC-blue?logo=github" alt="GitHub"></a>
        <img src="https://img.shields.io/badge/License-MPL%202.0-orange" alt="License">
      </p>
      <p>HTML5 VNC 客户端，用于在浏览器中提供远程桌面访问功能。</p>
      <p>
        <b>许可证：</b> <a href="https://www.mozilla.org/MPL/2.0/">Mozilla Public License 2.0</a><br>
        <b>源码：</b> <a href="https://github.com/novnc/noVNC">github.com/novnc/noVNC</a>
      </p>
      <details>
        <summary>⚖️ 许可证说明</summary>
        <p>本项目使用 noVNC 的未修改版本。根据 MPL 2.0 要求，若您修改了 noVNC 源代码，需将修改后的文件以 MPL 2.0 许可证开源。</p>
      </details>
    </td>
  </tr>
</table>



## 🤝 贡献与作者

- **作者**: 十月玩电脑
- **优化**: openclaw (ClaudeOpus), trea (Kimi-K2.5)

---

*活下去！活下去！活下去！在这反乌托邦里！*
