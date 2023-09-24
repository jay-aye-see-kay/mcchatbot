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

        python = pkgs.python3.withPackages (ps: [ ps.openai ]);

        mcchatbot = pkgs.python3Packages.buildPythonApplication {
          pname = "mcchatbot";
          version = "0.1";
          propagatedBuildInputs = [ pkgs.python3Packages.openai ];
          src = ./.;
        };

        dockerImage = pkgs.dockerTools.buildLayeredImage {
          name = "mcchatbot";
          tag = "0.1";
          config = { Cmd = [ "${mcchatbot}/bin/mcchatbot.py" ]; };
        };
      in
      {
        packages = {
          inherit python mcchatbot dockerImage;
        };

        devShells.default = pkgs.mkShell {
          buildInputs = [ python mcchatbot ];
        };
      });
    }
