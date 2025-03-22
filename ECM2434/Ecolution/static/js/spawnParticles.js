function spawnParticles(source, n, distance = 80, lifetime = 2500) {
    // Get boundaries of source element
    let source_rect = source.getBoundingClientRect();
    // Get center of the source_rect
    let centerX = source_rect.left + source_rect.width / 2;
    let centerY = source_rect.top + source_rect.height / 2;

    // Spawn n particles
    for (let i = 0; i < n; i++) {
        let {particle, startX, startY} = spawnParticle(source_rect);
        document.body.appendChild(particle);

        // Calculate the angle to fire the particle at
        let angle = Math.atan2(startY - centerY, startX - centerX)
        animateParticle(particle, angle, distance, lifetime);
    }
}

function spawnParticle(source_rect) {
    // Get a random particle source
    let size = Math.random() < 0.5 ? "large" : "small";
    let number = Math.floor(Math.random() * 7) + 1;

    let src = `${STATIC_IMAGES}particles/leaf_particles_${size}_${number}.png`;

    // Get a random starting location for the particle
    let startX = source_rect.left + Math.random() * source_rect.width;
    let startY = source_rect.top + Math.random() * source_rect.height;

    // Create the particle
    let particle = document.createElement("img");
    particle.classList.add("particle");
    particle.src = src;
    particle.width = 96;
    particle.style.opacity = 1;

    // Position the particle
    particle.style.left = `${startX - 48}px`;
    particle.style.top = `${startY - 48}px`;

    // Also returns the coordinates of the start, used in animation
    return {particle, startX, startY};
}

function animateParticle(particle, angle, distance, lifetime) {
    // Get a random distance
    let rand_distance = distance * (0.7 + Math.random() * 0.3) // Between 70% and 100% of original distance

    // Get the difference between current location and destination (change to ints for simpler translation)
    let diffX = Math.cos(angle) * rand_distance; // Adjacent = hypotenuse * sin(angle)
    let diffY = Math.sin(angle) * rand_distance; // Opposite = hypotenuse * cos(angle)

    // Set transition and timing of particle
    particle.style.transition = `transform ${lifetime}ms ease-out, opacity ${lifetime}ms ease-in-out`;

    // Apply CSS transition to particle
    requestAnimationFrame(() => {
        particle.style.transform = `translate(${diffX}px, ${diffY}px)`;
        particle.style.opacity = 0;
    });

    // Remove the particle after animation finished
    setTimeout(() => particle.remove(), lifetime);
}