// Función para mostrar la vista previa del archivo seleccionado
function previewFile(inputId, previewId) {
    const file = document.getElementById(inputId).files[0];
    const preview = document.getElementById(previewId);

    if (file) {
        const reader = new FileReader();
        reader.onload = function(e) {
            // Crear un objeto de tipo <embed> para mostrar el PDF
            const embed = document.createElement('embed');
            embed.src = e.target.result;
            embed.type = 'application/pdf';
            embed.width = '100%';
            embed.height = '500px'; // Ajusta el alto según sea necesario
            preview.innerHTML = '';
            preview.appendChild(embed);
            preview.style.display = 'block';
        };
        reader.readAsDataURL(file);
    } else {
        preview.innerHTML = '';
        preview.style.display = 'none';
    }
}

// Asociar la función previewFile a los eventos change de los inputs de archivo
document.getElementById('file1').addEventListener('change', function() {
    previewFile('file1', 'preview1');
});

document.getElementById('file2').addEventListener('change', function() {
    previewFile('file2', 'preview2');
});

// Mostrar el botón de carga y análisis cuando se cargan ambos archivos
document.getElementById('file1').addEventListener('change', function() {
    if (document.getElementById('file1').files.length > 0 && document.getElementById('file2').files.length > 0) {
        document.getElementById('analyzeBtn').style.display = 'block';
    }
});

document.getElementById('file2').addEventListener('change', function() {
    if (document.getElementById('file1').files.length > 0 && document.getElementById('file2').files.length > 0) {
        document.getElementById('analyzeBtn').style.display = 'block';
    }
});
