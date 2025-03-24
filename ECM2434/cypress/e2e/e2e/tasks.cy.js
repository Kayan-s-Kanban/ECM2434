describe('tasks spec', () => {
    beforeEach(() => {
      cy.login('testuser', 'password');
    });

    it('should allow a user to view assigned tasks', () => {
      cy.visit('/tasks');
      cy.contains('Your Tasks').should('be.visible');
    });

    it('should allow a user to complete a task and earn points', () => {
      cy.visit('/tasks');
      cy.contains('Buy groceries').parent().find('button.complete-task').click();
      cy.contains('Task completed successfully').should('be.visible');
      cy.contains('Points: 50').should('be.visible');
    });

    it('should increase user points when completing a task', () => {
      cy.visit('/tasks');
      cy.contains('Buy groceries').parent().find('button.complete-task').click();
      cy.contains('Points: 50').should('be.visible');
    });

    it('should level up the pet when gaining enough XP', () => {
      cy.visit('/profile');
      cy.contains('XP: 95');
      cy.completeTask('Buy groceries');
      cy.contains('Level: 2').should('be.visible');
    });

    it('should allow a user to view upcoming events', () => {
      cy.visit('/events');
      cy.contains('Upcoming Events').should('be.visible');
    });

    it('should allow a user to scan a QR code for an event', () => {
      cy.visit('/events');
      cy.get('button.scan-qr').click();
      cy.contains('QR code scanned successfully').should('be.visible');
    });
  });