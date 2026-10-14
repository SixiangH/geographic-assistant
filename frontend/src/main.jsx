import { createRoot } from "react-dom/client";
import { flushSync } from "react-dom";
import { buttonVariants } from "@/components/ui/button";
import App from "./App";
import "./theme.css";

function decorate(node, classes = "") {
  const tokens = classes.split(/\s+/);
  if (node.tagName === "BUTTON" && !tokens.includes("mention")) {
    const variant = tokens.includes("primary")
      ? "default"
      : tokens.includes("destructive")
        ? "destructive"
        : tokens.some((t) => ["text-button", "filter", "tab"].includes(t))
          ? "ghost"
          : "outline";
    node.classList.add(...buttonVariants({ variant, size: "sm" }).split(/\s+/));
    node.dataset.slot = "button";
    node.dataset.variant = variant;
  }
  if (
    node.tagName === "TEXTAREA" ||
    (node.tagName === "INPUT" && node.type !== "checkbox")
  )
    node.dataset.slot = node.tagName.toLowerCase();
}
window.atlasUI = { decorate };
window.atlasBootDeferred = true;
flushSync(() => createRoot(document.getElementById("root")).render(<App />));

// Classic scripts share the existing state and IndexedDB schema. Load them only after the shell commits.
// 现有脚本继续共享原有状态与 IndexedDB；页面框架提交后再按顺序加载。
async function boot() {
  for (const name of ["personal-store", "app", "library", "study"]) {
    await new Promise((resolve, reject) => {
      const script = document.createElement("script");
      const version = new URL(import.meta.url).pathname.split("/").pop();
      script.src = `/static/${name}.js?v=${encodeURIComponent(version)}`;
      script.async = false;
      script.onload = resolve;
      script.onerror = () =>
        reject(new Error(`Could not load ${name}. Please refresh the page.`));
      document.body.append(script);
    });
  }
  window.atlasBootDeferred = false;
  await window.start();
}
boot().catch((error) => {
  const status = document.getElementById("reading-status");
  if (status) {
    status.textContent = error.message;
    status.setAttribute("role", "alert");
  }
});
