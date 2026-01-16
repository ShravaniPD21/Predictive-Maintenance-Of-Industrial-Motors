### 📌 Project Details
- 🔹Predictive Maintenance of Industrial Motors: A system developed by integrating hardware and software such that the failures and faults in the motors would be predicted even before they occur!For hardware, STM32 nucleo F446ZE was used along with sensors like ACS712, ADXL345 & DHT22 as the parameters used were Current, Vibration, Temperature and Humidity respt. Hardware was coded on Arduino IDE and for backend Python was used. Software tech stack used was React Native, HTML, CSS,JS Python, Databases: Kaggle, MySQL and finally, the real time data received on the serail monitor of Arduino IDE was displayed on the dashboard made. For mobile display, ExpoGo was used.Main idea was that when the value of any of the parameter exceeds the threshold set, then the alerts would be send accordingly depending upon the conditions: normal, critical, alert!

# React + Vite

This template provides a minimal setup to get React working in Vite with HMR and some ESLint rules.

Currently, two official plugins are available:

- [@vitejs/plugin-react](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react) uses [Babel](https://babeljs.io/) (or [oxc](https://oxc.rs) when used in [rolldown-vite](https://vite.dev/guide/rolldown)) for Fast Refresh
- [@vitejs/plugin-react-swc](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react-swc) uses [SWC](https://swc.rs/) for Fast Refresh

## React Compiler

The React Compiler is not enabled on this template because of its impact on dev & build performances. To add it, see [this documentation](https://react.dev/learn/react-compiler/installation).

## Expanding the ESLint configuration

If you are developing a production application, we recommend using TypeScript with type-aware lint rules enabled. Check out the [TS template](https://github.com/vitejs/vite/tree/main/packages/create-vite/template-react-ts) for information on how to integrate TypeScript and [`typescript-eslint`](https://typescript-eslint.io) in your project.
