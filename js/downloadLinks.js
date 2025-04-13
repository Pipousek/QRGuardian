// Downloads functionality
const Downloads = {
    // Update download links with latest version from GitHub
    updateLinks: function() {
        // Get the latest release tag from GitHub
        fetch('https://api.github.com/repos/Pipousek/QRebuild/releases/latest')
            .then(response => response.json())
            .then(data => {
                const version = data.tag_name;
                
                // Update all download links
                const osTypes = ['Windows', 'macOS', 'Linux'];
                const appTypes = ['cli', 'gui'];
                
                osTypes.forEach(os => {
                    appTypes.forEach(app => {
                        const element = document.getElementById(`${os}-${app}-download`);
                        if (element) {
                            const appName = app.toUpperCase();
                            const osName = os === 'Windows' ? `${os}.exe` : os;
                            element.href = `https://github.com/Pipousek/QRebuild/releases/download/${version}/QRebuild-${appName}-${version}-${osName}`;
                            element.setAttribute('download', `QRebuild-${appName}-${version}-${osName}`);
                        }
                    });
                });
            })
            .catch(error => {
                console.error('Error fetching latest release:', error);
                // Fallback to a known version if API fails
                const fallbackVersion = '1.0.0';
                document.querySelectorAll('[id$="-download"]').forEach(el => {
                    const idParts = el.id.split('-');
                    const os = idParts[0];
                    const app = idParts[1];
                    const appName = app.toUpperCase();
                    const osName = os === 'Windows' ? `${os}.exe` : os;
                    el.href = `https://github.com/Pipousek/QRebuild/releases/download/${fallbackVersion}/QRebuild-${appName}-${fallbackVersion}-${osName}`;
                    el.setAttribute('download', `QRebuild-${appName}-${fallbackVersion}-${osName}`);
                });
            });
    }
};