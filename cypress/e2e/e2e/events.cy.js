describe('events spec', () => {
    before(() => {
      // Use your custom login command to log in
      cy.login('testuser', 'password');

      // After logging in, visit the event page
      cy.visit('http://127.0.0.1:8000/ecolution/events/');

      // Create an event via API (make sure you have an API endpoint for event creation)
      cy.request('POST', 'http://127.0.0.1:8000/api/events/', {
      title: 'Test Event',
      description: 'A test event for QR code validation',
      // Add other event properties as required by your Django model
      }).then((response) => {
      expect(response.status).to.eq(201); // Expect the event to be created successfully (HTTP 201 Created)
      eventId = response.body.id; // Capture the event ID from the response
      });
    });

    beforeEach(() => {
      // Visit the event page using the dynamically created event ID
      cy.visit(`/event/${eventId}`); // Replace with the correct URL format for your event page
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