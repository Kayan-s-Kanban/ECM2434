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
  (username, email, password, petName, agreeToTerms = false, petOption = null) => {
    cy.visit('http://127.0.0.1:8000/ecolution/signup/');

    // fill in the signup form
    cy.get('input[name="username"]').type(username);
    cy.get('input[name="email"]').type(email);
    cy.get('input[name="password1"]').type(password);
    cy.get('input[name="password2"]').type(password);

    // conditionally check the terms checkbox
    if (agreeToTerms) {
      cy.get('input[name="agree_terms"]').check();
    }

    // conditionally select a pet option
    if (petOption) {
        cy.get(`input[name="pet_type"][value="${petOption}"]`).check();
    }

    // conditionally select a pet option
    if (petName) {
        cy.get('input[name="pet_name"]').type(petName)
    }

    // submit form
    cy.get('button[type="submit"]').click();
  }
);

Cypress.Commands.add('deleteAccount', (username) => {
  cy.visit('/account/settings/delete_account');

  // click "delete account" button
  cy.get('button.delete').click();

  // check confirmation message (?)
  cy.contains('Account successfully deleted').should('be.visible');
});



