describe('Signup Spec', () => {
  it('should not be able to signup without agreeing to the T&C', () => {
    // try signing up without agreeing to Terms & Conditions
    cy.signup('testuser', 'testuser@example.com', 'TestPassword123!', false, 'mushroom', 'Shroomy');

    // check an error message appears for missing T&C agreement
    cy.contains('You must agree to the terms and conditions').should('be.visible');

    // Ensure user stays on the signup page
    cy.url().should('include', '/ecolution/signup/');
  });

  it('should be able to signup successfully when all fields are valid', () => {
    // try to sign up with valid details, pet selection, and T&C agreement
    cy.signup('validuser', 'validuser@example.com', 'ValidPassword123!', true, 'plant', 'Leafy');

    // check successful navigation
    cy.url().should('include', '/ecolution/home');

  });

  it('should not be able to signup without agreeing to T&C', () => {
    // enter signup details without agreeing to the T&C
    cy.signup('testuser', 'testuser@example.com', 'TestPassword123!', false, 'plant', 'leafy');

    // assert that an error message appears
    cy.contains('You must agree to the terms and conditions').should('be.visible');

    // check user stays on the signup page
    cy.url().should('include', '/ecolution/signup/');
  });

  it('should not be able to signup without selecting a pet', () => {
    // try signing up without selecting a pet
    cy.signup('testuser', 'testuser@example.com', 'TestPassword123!', true);

    // check error message appears for missing pet selection
    cy.contains('Please select a pet option').should('be.visible');

    // check user stays on the signup page
    cy.url().should('include', '/ecolution/signup/');
  });

  it('should not be able to signup without entering a pet name', () => {
    // select a pet but do NOT enter a pet name
    cy.signup('testuser2', 'testuser2@example.com', 'TestPassword123!', true, 'mushroom');

    // check that an error message appears for missing pet name
    cy.contains('Please enter a name for your pet').should('be.visible');

    // check user stays on the signup page
    cy.url().should('include', '/ecolution/signup/');
  });
});

describe('Signup, Login, and Delete Account Flow', () => {
  it('should be able to signup, login, and then delete account', () => {
    // signup
    cy.signup('testuser', 'testuser@example.com', 'TestPassword123!', true, 'mushroom', 'Shroomy');

    // check signup was successful
    cy.url().should('include', '/ecolution/home/');

    // logout
    cy.contains('Logout').click();
    cy.url().should('include', '/login');

    // login using same credentials (check that login works)
    cy.login('testuser', 'TestPassword123!');
    cy.url().should('include', '/dashboard');

    // delete account
    cy.deleteAccount('testuser');

    // check account deletion was successful
    cy.url().should('include', '/ecolution/login/'); // redirected to login page (?)
    cy.contains('Account successfully deleted').should('be.visible');

    // check login no longer works
    cy.login('testuser', 'TestPassword123!');
    cy.contains('Invalid username or password').should('be.visible');
  });
});
