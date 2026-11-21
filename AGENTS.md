# nginx-module-brotli

本仓库基于 nginx 官方 `nginx-module-image-filter` RPM 源码包（`.src.rpm`）改造，沿用官方动态模块的打包方式和基础编译参数，为 nginx 添加 Brotli 压缩支持：

* 使用 `ngx_brotli` 构建动态压缩模块和静态文件模块。
* 同时构建普通版和 debug 版动态模块。
* 使用 QuicTLS 源码参与构建，保留 HTTP/3 及现有发行版条件判断。
* 仅跟进 nginx mainline 版本，并与配套 nginx 的版本和构建参数保持兼容。

## 上游版本更新流程

1. 检查工作区和暂存区差异，保留已有的用户修改。
2. 从官方目录下载用户指定 nginx 版本对应的 `nginx-module-image-filter-<版本>-<发行号>.src.rpm`：
   https://nginx.org/packages/mainline/centos/9/SRPMS/
   未指定版本时，先明确目标版本，不凭本地文件推断最新版本。
3. 将源码包解压到仓库之外的临时目录。优先使用 `extract`；若不可用，可使用 `rpm2cpio` 配合 `cpio`。不要直接解包到仓库或覆盖现有文件。
4. 使用 `diff` 比较上游 `nginx-module-image-filter.spec` 与本地 `nginx-module-brotli.spec`，区分通用打包更新、image-filter 专属内容和本仓库定制，再逐项合并需要的变更。不要直接用上游文件整体覆盖本地文件。
5. 对 spec 逐段核对，合并上游变更的同时保留下述定制。必要时提取旧版官方源码包，以旧上游、新上游和本地文件进行三方比较。
6. 核对配套 nginx 仓库的目标版本、基础编译参数和 QuicTLS 版本，确保模块构建与目标 nginx 兼容。不要为同步本仓库而自动修改配套仓库。
7. 检查最终差异，确认修改与目标版本相关，且没有混入下载包、解包产物或构建产物。

## `nginx-module-brotli.spec` 合并要求

- 保留 Brotli 包名、描述、源码来源、文档目录和安装提示。不要引入 image-filter 专属的模块参数、依赖、文件路径或启用说明。
- 保留 `ngx_brotli` 的获取流程、固定提交和递归子模块更新。Brotli 源码升级与 nginx 升级分开判断，不因更新 nginx 而顺带跟进模块或子模块的新版本。
- 保留 `--add-dynamic-module`、`--with-compat`、两套模块编译步骤及 debug 模块重命名逻辑。继续使用 `make modules` 构建动态模块。
- 保留 QuicTLS 版本宏、源码地址、解包步骤，以及两处 `--with-openssl` 参数；保留 `--with-http_v3_module` 及相关发行版条件判断。
- 保留本地额外依赖和其他定制。不要仅因上游不存在对应内容就删除。
- 合并官方基础编译参数、通用依赖和打包逻辑的更新，避免遗漏新增内容。
- 核对 `base_version`、Release、Source 引用、解包目录和 `Requires: nginx-r%{base_version}`，确保模块依赖对应版本的 nginx，并保留版本化 Provides。
- 保留 `ngx_http_brotli_filter_module`、`ngx_http_brotli_static_module` 及其 debug 版本的安装；保留安装提示中两条普通版模块的 `load_module` 指令。
- 维护本仓库自己的 changelog，不用上游 image-filter 的包名和版本记录覆盖已有历史。

## 验证与交付

- 执行 `git diff --check`，并检查工作区与暂存区的最终差异。
- 修改 shell 脚本时，使用与脚本解释器匹配的语法检查。
- 有 RPM 工具和匹配的构建环境时，进行 spec 解析和相应构建验证，核对普通版与 debug 版的两个 Brotli 模块是否均已打包。
- 有配套 nginx 运行环境时，分别验证普通版和 debug 版模块加载、`nginx -t`、动态 Brotli 压缩和预压缩 `.br` 文件响应。
- 环境不具备时，明确说明未验证的项目，不把静态检查当作构建或运行成功。
- 完成后简要说明目标版本、合并的上游变化、保留的定制，以及实际执行的验证。
