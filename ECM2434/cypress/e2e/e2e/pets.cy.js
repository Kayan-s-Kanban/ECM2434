describe('pet actions spec', () => {
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

    it('should allow a user to create an account, complete a task, buy an accessory, and equip it', () => {
        // Step 1: Login
        cy.login(username, 'password123');

        // Check user is on Homepage
        cy.url().should('include', '/ecolution/home');

        // Navigate to tasks page
        cy.navigateToPage('/ecolution/tasks/')

        // Step 2: Complete a task to earn points
        cy.get('.task').first().contains('Complete Task').click();
        cy.wait(500);  // Wait for task completion

        // Check if points are updated
        cy.get('.user-points').should('contain', 'points: 110');  // Adjust based on expected points

        // Step 3: Buy an accessory using the earned points
        cy.visit('/shop');  // Visit the shop page

        // Find the accessory and buy it
        cy.get('.shop-item').first().should('contain', 'Accessory')
          .find('.buy-button').click();

        // Check if the purchase was successful
        cy.get('.purchase-success').should('contain', 'Purchase successful!');
        cy.get('.user-points').should('contain', 'points: 90');  // Adjust based on price of the item

        // Step 4: Equip the purchased accessory
        cy.visit('/select-accessory');  // Visit the accessory selection page

        // Equip the first accessory
        cy.get('.equip-accessory').first().click();

        // Verify the accessory was equipped
        cy.get('.pet-display').should('contain', 'Equipped Hat');
        cy.wait(500);
    });
});