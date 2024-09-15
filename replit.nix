{ pkgs }: {
    deps = [
        pkgs.python3
        pkgs.python3Packages.pip
        pkgs.python3Packages.virtualenv
    ];

    shellHook = ''
        if [ ! -d .venv ]; then
            virtualenv .venv
            source .venv/bin/activate
            pip install -r requirements.txt
        fi
        source .venv/bin/activate
    '';
}