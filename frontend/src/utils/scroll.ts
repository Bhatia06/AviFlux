export const scrollToFeatures = () => {
    const featuresSection = document.getElementById("features");
    if (featuresSection) {
        featuresSection.scrollIntoView({ behavior: "smooth" });
    }
};
