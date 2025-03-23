const { defineConfig } = require("cypress");

module.exports = defineConfig({
  e2e: {
    supportFile: false, // If you don't need a support file, leave this as false.
    specPattern: "cypress/e2e/e2e/*.js", // Update this to match the location of your spec files.
  },
});



