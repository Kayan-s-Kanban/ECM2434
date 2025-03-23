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
        cy.get('button[onclick="toggleUseMenu()"]').click(); // Open the menu
        cy.get('#mainMenu').should('be.visible'); // Verify menu is visible
        cy.get('a[href="/ecolution/home/"]').click(); // Click on "Home"
        cy.url().should('include', '/ecolution/home/');
    });

    it('should log in and navigate to Tasks', () => {
        cy.login(username, 'Password123!');
        cy.get('button[onclick="toggleUseMenu()"]').click(); // Open the menu
        cy.get('#mainMenu').should('be.visible'); // Verify menu is visible
        cy.get('a[href="/ecolution/tasks/"]').click(); // Click on "Tasks"
        cy.url().should('include', '/ecolution/tasks/');
    });

    it('should log in and navigate to Gamekeeper Tasks (if user is gamekeeper)', () => {
        // Log in as a gamekeeper
        cy.login(username, 'Password123!');
        cy.get('button[onclick="toggleUseMenu()"]').click(); // Open the menu
        cy.get('#mainMenu').should('be.visible'); // Verify menu is visible
        cy.get('a[href="/ecolution/gamekeeper_tasks/"]').click(); // Click on "Gamekeeper Tasks"
        cy.url().should('include', '/ecolution/gamekeeper_tasks/');
    });

    it('should log in and navigate to Events', () => {
        // Log in
        cy.login(username, 'Password123!');
        cy.get('button[onclick="toggleUseMenu()"]').click(); // Open the menu
        cy.get('#mainMenu').should('be.visible'); // Verify menu is visible
        cy.get('a[href="/ecolution/events/"]').click(); // Click on "Events"
        cy.url().should('include', '/ecolution/events/');
    });

    it('should log in and navigate to Shop', () => {
        // Log in
        cy.login(username, 'Password123!');
        cy.get('button[onclick="toggleUseMenu()"]').click(); // Open the menu
        cy.get('#mainMenu').should('be.visible'); // Verify menu is visible
        cy.get('a[href="/ecolution/shop/"]').click(); // Click on "Shop"
        cy.url().should('include', '/ecolution/shop/');
    });

    it('should log in and navigate to Leaderboard', () => {
        // Log in
        cy.login(username, 'Password123!');
        cy.get('button[onclick="toggleUseMenu()"]').click(); // Open the menu
        cy.get('#mainMenu').should('be.visible'); // Verify menu is visible
        cy.get('a[href="/ecolution/leaderboard/"]').click(); // Click on "Leaderboard"
        cy.url().should('include', '/ecolution/leaderboard/');
    });

    it('should log in and navigate to QR Code Scanner', () => {
        // Log in
        cy.login(username, 'Password123!');
        cy.get('button[onclick="toggleUseMenu()"]').click(); // Open the menu
        cy.get('#mainMenu').should('be.visible'); // Verify menu is visible
        cy.get('a[href="/ecolution/qr_scanner/"]').click(); // Click on "QR Code Scanner"
        cy.url().should('include', '/ecolution/qr_scanner/');
    });

    it('should log in and navigate to Settings', () => {
        // Log in
        cy.login(username, 'Password123!');
        cy.get('button[onclick="toggleUseMenu()"]').click(); // Open the menu
        cy.get('#mainMenu').should('be.visible'); // Verify menu is visible
        cy.get('a[href="/ecolution/settings/"]').click(); // Click on "Settings"
        cy.url().should('include', '/ecolution/settings/');
    });

    it('should not allow login with incorrect credentials', () => {
        // Try to login with incorrect credentials
        cy.login(username, 'wrongpassword');

        // Assert that error message is displayed
        cy.contains('Invalid username or password').should('be.visible');
    });

    it('should allow a user to log out', () => {
        // login
        cy.login(username, 'Password123!');

        // Ensure user is on "Settings" page
        cy.url().should('include', '/ecolution/settings');

        // Log out
        cy.get('#logout-button').click();

        // Ensure user is redirected to login page
        cy.contains('Login').should('be.visible');
    });
});

describe('Security & Permissions', () => {
    it('should not allow unauthenticated users to access protected pages', () => {
        // Visit a page that requires authentication (like tasks)
        cy.visit('/tasks');

        // Ensure the user is prompted to log in
        cy.contains('Please log in').should('be.visible');
    });
});



