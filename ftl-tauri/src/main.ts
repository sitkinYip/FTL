import { createApp } from "vue";
import { createPinia } from "pinia";
import naive from "naive-ui";
import App from "./App.vue";
import { lightTheme, darkTheme } from "naive-ui";
import "./styles/global.css";

const app = createApp(App);
app.use(createPinia());
app.use(naive);

// 跟随系统外观
const mediaQuery = window.matchMedia("(prefers-color-scheme: dark)");
app.provide("theme", mediaQuery.matches ? darkTheme : lightTheme);
mediaQuery.addEventListener("change", (e) => {
  app.provide("theme", e.matches ? darkTheme : lightTheme);
});

app.mount("#app");
