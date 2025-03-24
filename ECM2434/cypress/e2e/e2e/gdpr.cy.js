describe('GDPR & PP', () => {
    it('should navigate to GDPR + PP from Signup', () => {
        cy.visit('http://127.0.0.1:8000/ecolution/signup/');
        // check user is on "Signup" page
        cy.url().should('include', '/ecolution/signup/');

        // user selects T&C link

        // check user is on "GDPR" and "PP" page
        cy.url().should('include', '/ecolution/term_of_use')

    });

    it('should navigate to GDPR + PP after logging in', () => {
        // login
        cy.login('testuser', 'password');

        // check user is on "Settings" page
        cy.url().should('include', '/ecolution/settings/');

        // check user is able to view GDPR and PP
        cy.url().should('include', '/ecolution/term_of_use/');
    });

    it('should be able to view GDPR (PDF)', () => {
        // login
        cy.login('testuser', 'password');

        // check user is on "Home" page
        cy.url().should('include', '/ecolution/home/');

        // check user is on "Settings" page
        cy.url().should('include', '/ecolution/settings/');

        // check user is able to view GDPR and PP
        cy.url().should('include', '/ecolution/term_of_use/');

        // check user is able to view GDPR pdf via link
        cy.url().should('include', '/ecolution/term_of_user/T&C_Sprint_1_(PDF).pdf')
    });

    it('should be able to view PP (PDF)', () => {
        // login
        cy.login('testuser', 'password');

        // check user is on "Home" page
        cy.url().should('include', '/ecolution/home/');

        // check user is on "Settings" page
        cy.url().should('include', '/ecolution/settings/');

        // check user is able to view GDPR and PP
        cy.url().should('include', '/ecolution/term_of_use/');

        // check user is able to view GDPR pdf via link
        cy.url().should('include', '/ecolution/term_of_user/PP_Sprint_1_(PDF).pdf')
        cy.wait(500);
    });
});