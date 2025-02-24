(function(){

    function getCSRFToken() {
        return document.cookie.match(/csrftoken=([^;]+)/)[1];
    }

    window.completeTask = function(element, taskId) {
        fetch(`/ecolution/tasks/complete/${taskId}/`, {
            method: 'POST',
            headers: { 
                'X-CSRFToken': getCSRFToken()
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === "success") {
                var pointsEl = document.querySelector(".currency_indicator h3");
                if (pointsEl) { 
                    pointsEl.innerText = data.points; 
                }
                var taskElement = element.closest(".task");
                if (taskElement) {
                    taskElement.remove();
                }
                if (window.location.href.includes("tasks")) {
                    window.location.href = "/ecolution/tasks/";
                } else {
                    window.location.href = "/ecolution/home/";
                }
            }
        })
        .catch(error => console.error('Error completing task:', error));
    };    
    

    window.deleteTask = function(element, userTaskId) {
        fetch(`/ecolution/tasks/delete/${userTaskId}/`, {
            method: 'POST',
            headers: { 
                'X-CSRFToken': getCSRFToken()
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === "success") {
                var taskElement = element.closest(".task");
                if(taskElement) { taskElement.remove(); }
            }
        })
        .catch(error => console.error('Error deleting task:', error));
    };
})();
