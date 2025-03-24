// ***********************************************
// This example commands.js shows you how to
// create various custom commands and overwrite
// existing commands.
//
// For more comprehensive examples of custom
// commands please read more here:
// https://on.cypress.io/custom-commands
// ***********************************************
//
//
// -- This is a parent command --
// Cypress.Commands.add('login', (email, password) => { ... })
//
//
// -- This is a child command --
// Cypress.Commands.add('drag', { prevSubject: 'element'}, (subject, options) => { ... })
//
//
// -- This is a dual command --
// Cypress.Commands.add('dismiss', { prevSubject: 'optional'}, (subject, options) => { ... })
//
//
// -- This will overwrite an existing command --
// Cypress.Commands.overwrite('visit', (originalFn, url, options) => { ... })

import '@cypress/code-coverage/support';

Cypress.Commands.add('login', (username, password) => {
    cy.visit('http://127.0.0.1:8000/ecolution/login/');

    // select and enter username
    cy.get('input[name="username"]').type(username);

    // select and enter password
    cy.get('input[name="password"]').type(password);

    // select submit button
    cy.get('button[type="submit"]').click();
});

Cypress.Commands.add(
  'signup',
  (email, password, petOption = 'mushroom', petName = '', agreeToTerms = false) => {
    cy.visit('http://127.0.0.1:8000/ecolution/signup/');

    const username = `user_${Date.now()}`;  // Generate a unique username

    // Fill in the signup form
    cy.get('input[name="username"]').type(username);

    if (email) {
        cy.get('input[name="email"]').type(email);
    }
    cy.get('input[name="password1"]').type(password);
    cy.get('input[name="password2"]').type(password);

    // If pet type is provided (petOption is defaulted to mushroom)
    if (petOption) {
        cy.get(`input[name="pet_type"][value="${petOption}"]`).check({ force: true });
        if (petName) {
            cy.get('input[name="pet_name"]').should('be.visible').type(petName, { force: true });
        }
    }

    // Check the terms checkbox if needed
    if (agreeToTerms) {
      cy.get('input[name="agree_terms"]').check();
    }

    // Submit the form
    cy.get('button[type="submit"]').click();

    // Wrap the username in a chainable and return it using `cy.wrap()`
    cy.wrap(username).as('username');
  }
);

Cypress.Commands.add('navigateToPage', (pageUrl) => {
    // Open the menu and verify it's visible
    cy.get('button[onclick="toggleUseMenu()"]').should('be.visible').click();

    // Wait for the menu to be visible
    cy.get('#mainMenu').should('be.visible');

    // Click on the first link corresponding to the pageUrl
    cy.get(`a[href="${pageUrl}"]`).first().click();

    // Wait for page load and verify that the URL is correct
    cy.url().should('include', pageUrl);
});

Cypress.Commands.add('deleteAccount', (username) => {
  cy.visit('/account/settings/delete_account');

  // click "delete account" button
  cy.get('button.delete').click();

  // check confirmation message (?)
  cy.contains('Account successfully deleted').should('be.visible');
});



