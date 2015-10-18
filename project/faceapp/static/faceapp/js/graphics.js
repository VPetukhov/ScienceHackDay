(function () {
    var container;
    var camera, scene, renderer;
    var prevX, prevY;
    var zoomInInterval, zoomOutInterval;
    var mouseDown;
    var face;

    document.addEventListener('mousedown', onDocumentMouseDown, false);
    document.addEventListener('mouseup', onDocumentMouseUp, false);

    $('#zoomin').mousedown(onZoomInDown);
    $('#zoomout').mousedown(onZoomOutDown);

    init();
    animate();

    $('#fileinput').on('submit', 'form', function (e) {
        e.preventDefault();
        console.log($(this).attr('action'));
        $.ajax({
            url: $(this).attr('action'),
            method: 'POST',
            data: new FormData(this),
            processData: false,
            contentType: false
        }).then(function (data) {
                var loader = new THREE.OBJLoader();
                var object = loader.parse(data);
                scene.remove(face);
                face = object;
                scene.add(face);
            }
            , function (err) {
                console.log(err);
            })
    })

    function init() {

        container = document.createElement('div');
        document.body.appendChild(container);

        camera = new THREE.PerspectiveCamera(45, window.innerWidth / window.innerHeight, 1, 2000);
        camera.position.z = 5;
        scene = new THREE.Scene();

        var ambient = new THREE.AmbientLight(0x101030);
        scene.add(ambient);

        var directionalLight = new THREE.DirectionalLight(0xffeedd);
        directionalLight.position.set(0, 0, 1);
        scene.add(directionalLight);

        var manager = new THREE.LoadingManager();
        manager.onProgress = function (item, loaded, total) {
            console.log(item, loaded, total);
        };

        var texture = new THREE.Texture();

        var onProgress = function (xhr) {
            if (xhr.lengthComputable) {
                var percentComplete = xhr.loaded / xhr.total * 100;
                console.log(Math.round(percentComplete, 2) + '% downloaded');
            }
        };

        var onError = function (xhr) {
        };

        var loader = new THREE.OBJLoader(manager);
        loader.load('/static/faceapp/models/SLC35D.obj', function (object) {
            face = object;
            object.position.y = 0;
            scene.add(object);

        }, onProgress, onError);

        renderer = new THREE.WebGLRenderer();
        renderer.setPixelRatio(window.devicePixelRatio);
        renderer.setSize(window.innerWidth, window.innerHeight);
        container.appendChild(renderer.domElement);

        document.addEventListener('mousemove', onDocumentMouseMove, false);
        window.addEventListener('resize', onWindowResize, false);
    }

    function onWindowResize() {
        windowHalfX = window.innerWidth / 2;
        windowHalfY = window.innerHeight / 2;

        camera.aspect = window.innerWidth / window.innerHeight;
        camera.updateProjectionMatrix();

        renderer.setSize(window.innerWidth, window.innerHeight);
    }

    function onDocumentMouseDown(e) {
        mouseDown = true;
        prevX = e.clientX;
        prevY = e.clientY;
    }

    function onDocumentMouseUp(e) {
        mouseDown = false;
        clearInterval(zoomInInterval);
        clearInterval(zoomOutInterval);
    }

    function onZoomInDown() {
        zoomInInterval = setInterval(function () {
            camera.position.z -= 0.1;
        }, 10);
    }

    function onZoomOutDown() {
        zoomOutInterval = setInterval(function () {
            camera.position.z += 0.1;
        }, 10);
    }

    function onDocumentMouseMove(event) {
        event.preventDefault();
        if (mouseDown) {
            var dX = event.clientX - prevX;
            var dY = event.clientY - prevY;

            face.rotateOnAxis(face.worldToLocal(new THREE.Vector3(1, 0, 0)), dY * 0.002);
            face.rotateOnAxis(face.worldToLocal(new THREE.Vector3(0, 1, 0)), dX * 0.002);

            prevX = event.clientX;
            prevY = event.clientY;
        }
    }

    function animate() {
        requestAnimationFrame(animate);
        render();
    }

    function render() {
        renderer.render(scene, camera);
    }

})()
