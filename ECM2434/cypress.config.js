const { defineConfig } = require("cypress");

module.exports = defineConfig({
  e2e: {
    specPattern: "cypress/e2e/e2e/*.cy.js", // Corrected path for your spec files.
    supportFile: 'cypress/support/e2e.js', // Ensure it's pointing to e2e.js
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




