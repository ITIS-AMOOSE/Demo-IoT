// Node-RED Settings - Tắt mã hóa credentials cho demo
module.exports = {
    credentialSecret: "",
    flowFile: 'flows.json',
    uiPort: process.env.PORT || 1880,
    diagnostics: { enabled: true, ui: true },
    logging: {
        console: {
            level: "info",
            metrics: false,
            audit: false
        }
    },
    editorTheme: {
        projects: { enabled: false }
    }
};
