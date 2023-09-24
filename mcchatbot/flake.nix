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
      in
      {
        packages = {
          python = pkgs.python3.withPackages (ps: [ ps.openai ]);

          mcchatbot = pkgs.python3Packages.buildPythonApplication {
            pname = "mcchatbot";
            version = "1.0";
            propagatedBuildInputs = [ pkgs.python3Packages.openai ];
            src = ./.;
          };
        };
      });
}
