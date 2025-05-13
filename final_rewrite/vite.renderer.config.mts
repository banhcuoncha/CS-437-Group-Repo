import { defineConfig } from "vite";

// https://github.com/tailwindlabs/tailwindcss/discussions/16250
// eslint-disable-next-line @typescript-eslint/ban-ts-comment
// @ts-ignore
// eslint-disable-next-line import/no-unresolved
import tailwindcss from "@tailwindcss/vite";
import vue from "@vitejs/plugin-vue";

// https://vitejs.dev/config
export default defineConfig({
  root: "src/renderer",
  plugins: [tailwindcss(), vue()],
});
