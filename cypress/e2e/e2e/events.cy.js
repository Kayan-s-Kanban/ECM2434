describe('events spec', () => {
    before(() => {
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

            cy.get('button[onclick="toggleUseMenu()"]').click(); // Open the menu
            cy.get('#mainMenu').should('be.visible'); // Verify menu is visible
            cy.get('a[href="/ecolution/events/"]').click(); // Click on "Events"
            cy.url().should('include', '/ecolution/events/');
        });

        cy.get('input[name="event_name"]').type('Beach Cleanup');
        cy.get('input[name="description"]').type('Join us for a beach cleanup event.');
        cy.get('input[name="location"]').type('Santa Monica Beach');
        cy.get('input[name="date"]').type('2025-05-20');
        cy.get('input[name="time"]').type('10:00');
        cy.get('button[type="submit"]').click();
        cy.url().should('include', '/ecolution/createevent/');
    });

    it('should be able to delete a created event', () => {
        // Assuming the event is already created and visible on the page
        cy.get('.event').first().click(); // Click on the event
        cy.get('button#delete-event').click(); // Click on the delete button

        // Verify the event is deleted
        cy.contains('Event deleted successfully').should('be.visible');
    });

    it('should be able to join an event and complete tasks', () => {
        // Join an event
        cy.get('.event').first().click(); // Click on an event
        cy.get('#button').click(); // Click on Join Event

        // Verify the event is joined
        cy.contains('You have successfully joined the event').should('be.visible');

        // Complete tasks
        cy.get('.taskcard').first().find('input[type="checkbox"]').check(); // Check a task

        // Verify that task completion updates
        cy.get('.taskcard').first().find('input[type="checkbox"]').should('be.checked');
    });

    it('should be able to join an event, complete tasks, and complete event through QR validation', () => {
        cy.get('.event').first().click();
        cy.get('#button').click(); // Join the event

        // Simulate task completion
        cy.get('.taskcard').first().find('input[type="checkbox"]').check();

        // Simulate QR code validation
        cy.get('#qr-code-input').type('validQRCode1234');
        cy.get('#validate-button').click();

        // Complete the event
        cy.get('#complete-event-button').click();

        // Verify event completion
        cy.contains('Event completed successfully').should('be.visible');
    });

    it('should not be able to complete event without QR validation', () => {
        cy.get('.event').first().click();
        cy.get('#button').click(); // Join the event

        // Attempt to complete event without QR validation
        cy.get('#complete-event-button').click();

        // Verify error message
        cy.contains('QR code is required to complete the event').should('be.visible');
    });

    it('should navigate back to events page from event page', () => {
        // Ensure the back navigation works
        cy.get('a[href="/ecolution/events/"]').click();
        cy.url().should('include', '/ecolution/events/');
    });

    it('should allow event completion if the correct QR code is validated', () => {
        // Simulate QR code scanning by entering a valid QR code
        cy.get('#qr-code-input').type('validQRCode1234'); // Replace with valid QR code value
        cy.get('#validate-button').click(); // Click the button to validate the QR code

        // Check if the event completion button is enabled after QR code validation
        cy.get('#complete-event-button').should('not.be.disabled');

        // Attempt to complete the event by clicking the button
        cy.get('#complete-event-button').click();

        // Verify the success message or state after completing the event
        cy.contains('Event completed successfully').should('be.visible'); // Replace with actual success message
    });

    it('should not allow event completion with an incorrect or unvalidated QR code', () => {
        // Test for incorrect QR code
        cy.get('#qr-code-input').type('invalidQRCode'); // Replace with an incorrect QR code
        cy.get('#validate-button').click(); // Click to validate

        // Ensure the event completion button is disabled when the QR code is invalid
        cy.get('#complete-event-button').should('be.disabled');

        // Verify that an error message shows for invalid QR code
        cy.contains('Invalid QR code. Please try again').should('be.visible'); // Replace with your app's actual error message

        // Test for no QR code entered
        cy.get('#qr-code-input').clear(); // Clear the QR code input field
        cy.get('#complete-event-button').click(); // Try to complete the event without entering a QR code

        // Ensure that the event cannot be completed without entering a QR code
        cy.contains('QR code is required to complete the event').should('be.visible'); // Replace with the correct message for no QR code
    });
});
