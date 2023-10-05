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

        version = builtins.replaceStrings
          [ "\n" ]
          [ "" ]
          (builtins.readFile ./version);

        python = pkgs.python311.withPackages (p: [
          p.openai
          p.pydantic
          p.docker
        ]);

        mcchatbot = pkgs.python311Packages.buildPythonApplication {
          inherit version;
          pname = "mcchatbot";
          propagatedBuildInputs = [ python ];
          src = ./.;
        };

        buildImage = extraConfig: pkgs.dockerTools.buildImage ({
          name = "jayayeseekay/mcchatbot";
          tag = "latest";
          config = {
            Cmd = [ "${mcchatbot}/bin/mcchatbot.py" ];
            Env = [ "TZDIR=${pkgs.tzdata}/share/zoneinfo" ];
          };
        } // extraConfig);
      in
      {
        packages = {
          inherit python mcchatbot;
          buildx86Image = buildImage { architecture = "amd64"; };
          buildArmImage = buildImage { architecture = "arm64"; };
        };

        devShells.default = pkgs.mkShell {
          buildInputs = [
            python

            # to inspect the database
            pkgs.sqlite

            # repeating these to keep python lsp happy
            pkgs.python311Packages.openai
            pkgs.python311Packages.pydantic
            pkgs.python311Packages.docker

            # dev tools
            pkgs.just
            pkgs.python311Packages.isort
            pkgs.python311Packages.black
          ];
        };
      });
}
