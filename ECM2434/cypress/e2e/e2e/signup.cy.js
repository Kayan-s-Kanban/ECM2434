describe('Signup Spec', () => {
  it('should not be able to signup without agreeing to the T&C', () => {
    // Try signing up without agreeing to Terms & Conditions
    cy.signup('testuser@example.com', 'Password123!', 'mushroom', 'testPet', false); // changed agreeToTerms to false

    // Ensure user stays on the signup page
    cy.url().should('include', '/ecolution/signup/');
  });

  it('should be able to signup successfully when all fields are valid', () => {
    // Try to sign up with valid details, pet selection, and T&C agreement
    cy.signup('testuser@example.com', 'Password123!', 'mushroom', 'Shroomy', true);

    // Check if signup was successful by verifying navigation to the login page
    cy.url().should('include', '/ecolution/login');
  });

  it('should not be able to signup without selecting a pet', () => {
    // Try signing up without selecting a pet
    cy.signup('testuser@example.com', 'Password123!', '', 'Shroomy', true);

    // Ensure user stays on the signup page
    cy.url().should('include', '/ecolution/signup/');
  });

  it('should not be able to signup without entering a pet name', () => {
    // Select a pet but do NOT enter a pet name
    cy.signup('testuser@example.com', 'Password123!', 'mushroom', '', true);

    // Ensure user stays on the signup page
    cy.url().should('include', '/ecolution/signup/');
  });

  it('should not be able to signup with an invalid email format', () => {
    // Try signing up with an invalid email
    cy.signup('invalidemail', 'Password123!', 'mushroom', 'Shroomy', true);

    // Ensure user stays on the signup page
    cy.url().should('include', '/ecolution/signup/');

    // Check if email validation error is shown
    // cy.contains('Please enter a valid email address.').should('be.visible');
  });

  it('should not be able to signup without entering an email', () => {
    // Try signing up with an empty email
    cy.signup('', 'Password123!', 'mushroom', 'Shroomy', true);

    // Ensure user stays on the signup page
    cy.url().should('include', '/ecolution/signup/');

    // Check if email error is shown
    // cy.contains('Please enter a valid email address.').should('be.visible');
  });

  it('should not be able to signup with a weak password', () => {
    // Try signing up with a weak password (e.g., too short)
    cy.signup('testuser@example.com', 'pass', 'mushroom', 'Shroomy', true);

    // Ensure user stays on the signup page
    cy.url().should('include', '/ecolution/signup/');

    // Check if password error is shown
    // cy.contains('This password is too short').should('be.visible');
  });

  it('should be able to login immediately after signup', () => {
    // Sign up with valid details
    cy.signup('testuser@example.com', 'Password123!', 'mushroom', 'Shroomy', true);

    // Ensure the user is redirected to the login page
    cy.url().should('include', '/ecolution/login');

    // Access the stored username using the alias
    cy.get('@username').then((username) => {
      // Ensure the username is a string (in case of any issues with the alias)
      expect(username).to.be.a('string');

      // Try logging in with the same username and password
      cy.login(username, 'Password123!');

      // Ensure successful login and redirection to the home page
      cy.url().should('include', '/ecolution/home');
  });
});

});
