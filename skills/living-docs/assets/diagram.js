// Mermaid 初始化（经典脚本，非 module）。
// 必须在本文件之前用 <script src="…/assets/mermaid.min.js"></script> 加载全局 mermaid。
// 用经典脚本而非 ESM import：file:// 下浏览器禁止 module 的跨源/本地 import，
// 经典脚本 + 本地 vendored mermaid 才能在双击打开的 HTML 里正常渲染。
(function () {
  if (!window.mermaid) {
    console.warn("[diagram] mermaid 未加载，图将显示为源码");
    return;
  }
  mermaid.initialize({
    startOnLoad: true,
    theme: "neutral",
    securityLevel: "loose", // 允许节点标签里的 <br/> 换行
    flowchart: { curve: "basis", useMaxWidth: true, htmlLabels: true },
    sequence: { useMaxWidth: true },
    themeVariables: {
      fontFamily:
        '-apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", "Microsoft YaHei", sans-serif',
      fontSize: "14px",
      primaryColor: "#eef5ff",
      primaryBorderColor: "#0b64d8",
      lineColor: "#666b73",
    },
  });
})();
