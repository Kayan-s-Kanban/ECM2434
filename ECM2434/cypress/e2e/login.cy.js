describe('Login and Navigate', () => {
    it('should log in and navigate to Home', () => {
        // login
        cy.login('testuser', 'password');

        // check user is on "Home" page
        cy.url().should('include', '/ecolution/home/');
    });

    it('should log in and navigate to Tasks', () => {
        // login
        cy.login('testuser', 'password');

        // check user is on "Tasks" page
        cy.url().should('include', '/ecolution/tasks/');
    });

    it('should log in and navigate to Settings', () => {
        // login
        cy.login('testuser', 'password');

        // check user is on "Settings" page
        cy.url().should('include', '/ecolution/settings/');
    });

    it('should log in and navigate to Events', () => {
        // login
        cy.login('testuser', 'password');

        // check user is on "Home" page
        cy.url().should('include', '/ecolution/events/');
    });

    it('should log in and navigate to Delete Account page', () => {
        // login
        cy.login('testuser', 'password');

        // check user is on "Delete Account" page
        cy.url().should('include', '/ecolution/delete-account/');
    });

    it('should log in and navigate to Add Tasks page', () => {
        // login
        cy.login('testuser', 'password');

        // check user is on "Add Task" page
        cy.url().should('include', '/ecolution/tasks/add/');
    });

    it('should log in and navigate to Delete Task page', () => {
        // login
        cy.login('testuser', 'password');

        // TODO: user selects task to delete

        // check user is on "Delete Task" page
        cy.url().should('include', '/ecolution/tasks/delete/{user_task_id}');
    });

});
