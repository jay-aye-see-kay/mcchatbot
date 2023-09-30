{
  description = "";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};

        # IMPORTANT: keep in sync with version in ./setup.py
        mccVersion = "0.2";

        python = pkgs.python311.withPackages (p: [
          p.openai
          p.pydantic
          p.docker
        ]);

        mcchatbot = pkgs.python311Packages.buildPythonApplication {
          pname = "mcchatbot";
          version = mccVersion;
          propagatedBuildInputs = [ python ];
          src = ./.;
        };

        dockerImage = pkgs.dockerTools.buildLayeredImage {
          name = "jayayeseekay/mcchatbot";
          tag = mccVersion;
          config = { Cmd = [ "${mcchatbot}/bin/mcchatbot.py" ]; };
        };
      in
      {
        packages = {
          inherit python mcchatbot dockerImage;
        };

        devShells.default = pkgs.mkShell {
          buildInputs = [ python pkgs.sqlite ];
        };
      });
}
