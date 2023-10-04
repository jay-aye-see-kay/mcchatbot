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

        buildx86Image = pkgs.dockerTools.buildImage {
          name = "jayayeseekay/mcchatbot";
          tag = "latest";
          architecture = "amd64";
          config = { Cmd = [ "${mcchatbot}/bin/mcchatbot.py" ]; };
        };

        buildArmImage = pkgs.dockerTools.buildImage {
          name = "jayayeseekay/mcchatbot";
          tag = "latest-arm64";
          architecture = "arm64";
          config = { Cmd = [ "${mcchatbot}/bin/mcchatbot.py" ]; };
        };
      in
      {
        packages = {
          inherit python mcchatbot buildx86Image buildArmImage;
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
