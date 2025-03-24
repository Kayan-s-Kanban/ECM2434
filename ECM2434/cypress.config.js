const { defineConfig } = require("cypress");

module.exports = defineConfig({
  e2e: {
    supportFile: false, // If you don't need a support file, leave this as false.
    specPattern: "cypress/e2e/**/*.js", // Corrected path for your spec files.
    env: {
      coverage: true,  // Enabling code coverage collection
    },
    setupNodeEvents(on, config) {
      // Integrating code coverage
      require('@cypress/code-coverage/task')(on, config);
      return config;
    },
  },
});




