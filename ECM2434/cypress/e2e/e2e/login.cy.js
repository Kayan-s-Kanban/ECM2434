describe('Login and Navigate', () => {
    let username;

    before(() => {
        // Sign up for account prior
        cy.signup('testuser@example.com', 'Password123!', 'mushroom', 'Shroomy', true);

        // Retrieve the dynamically generated username
        cy.get('@username').then((user) => {
            username = user;
        });

        // Check if signup was successful by verifying navigation to the login page
        cy.url().should('include', '/ecolution/login');
    });

   it('should log in and navigate to Home', () => {
        cy.login(username, 'Password123!');
        cy.wait(500);
        cy.url().should('include', '/ecolution/home/');
    });

    it('should log in and navigate to Tasks', () => {
        cy.login(username, 'Password123!');
        cy.navigateToPage('/ecolution/tasks/')
        cy.url().should('include', '/ecolution/tasks/');
    });

    it('should log in and navigate to Events', () => {
        // Log in
        cy.login(username, 'Password123!');
        cy.navigateToPage('/ecolution/events/');
        cy.url().should('include', '/ecolution/events/');
    });

    it('should log in and navigate to Shop', () => {
        // Log in
        cy.login(username, 'Password123!');
        cy.navigateToPage('/ecolution/shop/');
        cy.url().should('include', '/ecolution/shop/');
    });

    it('should log in and navigate to Leaderboard', () => {
        // Log in
        cy.login(username, 'Password123!');
        cy.navigateToPage('/ecolution/leaderboard');
        cy.url().should('include', '/ecolution/leaderboard/');
    });

    it('should log in and navigate to QR Code Scanner', () => {
        // Log in
        cy.login(username, 'Password123!');
        cy.navigateToPage('/ecolution/qr_scanner');
        cy.url().should('include', '/ecolution/qr_scanner/');
    });

    it('should log in and navigate to Settings', () => {
        // Log in
        cy.login(username, 'Password123!');
        cy.navigateToPage('/ecolution/settings/');
        cy.url().should('include', '/ecolution/settings/');
    });

    it('should not allow login with incorrect credentials', () => {
        // Try to login with incorrect credentials
        cy.login(username, 'wrongpassword');

        // Assert that user is still on login page
        cy.should(url().should('include', '/ecolution/login'));
    });

    it('should allow a user to log out', () => {
        // login
        cy.login(username, 'Password123!');

        // Navigate to settings page
        cy.navigateToPage('/ecolution/settings/')

        // Click the logout button
        cy.get('button[onclick*="location.href"]').second().click(); // Click the logout button

        // Verify that the user is redirected to the login page (or another page after logout)
        cy.url().should('include', '/ecolution/login');
    });
});