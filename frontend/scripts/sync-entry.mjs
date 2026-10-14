import { copyFile } from "node:fs/promises";
await copyFile(
  new URL("../../app/static/ui/index.html", import.meta.url),
  new URL("../../app/static/index.html", import.meta.url),
);
console.log("Updated the FastAPI entry page.");
