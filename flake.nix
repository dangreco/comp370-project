{
  description = "comp370 project environment";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-parts.url = "github:hercules-ci/flake-parts";
  };

  outputs =
    inputs@{ flake-parts, ... }:
    flake-parts.lib.mkFlake { inherit inputs; } {
      systems = [
        "x86_64-linux"
        "aarch64-linux"
        "aarch64-darwin"
        "x86_64-darwin"
      ];
      perSystem =
        {
          pkgs,
          ...
        }:
        {
          devShells = {
            default =
              let
                latex = (
                  pkgs.texliveSmall.withPackages (
                    ps: with ps; [
                      latexmk
                      chktex
                      courier
                      algorithms
                      latexindent
                    ]
                  )
                );
                __zed = pkgs.writeTextFile {
                  name = "__zed";
                  text = builtins.toJSON {
                    lsp = {
                      ty = {
                        binary = {
                          path = "${pkgs.ty}/bin/ty";
                          arguments = [ "server" ];
                        };
                      };
                      texlab = {
                        path = "${pkgs.texlab}/bin/texlab";
                        settings.texlab.build = {
                          executable = "${latex}/bin/latexmk";
                          args = [
                            "-pdf"
                            "-interaction=nonstopmode"
                            "-synctex=1"
                            "%f"
                          ];
                          onSave = false;
                        };
                      };
                    };
                    languages = {
                      Python = {
                        language_servers = [
                          "!pylsp"
                          "!pyright"
                          "!basedpyright"
                          "ty"
                        ];
                        formatter = {
                          external = {
                            command = "${pkgs.ruff}/bin/ruff";
                            arguments = [
                              "format"
                              "--stdin-filename"
                              "{buffer_path}"
                            ];
                          };
                        };
                      };
                      LaTeX = {
                        formatter = {
                          external = {
                            command = "${pkgs.tex-fmt}/bin/tex-fmt";
                            arguments = [ "--stdin" ];
                          };
                        };
                      };
                    };
                  };
                  destination = "/settings.json";
                };
                libraryPath =
                  with pkgs;
                  lib.makeLibraryPath [
                    stdenv.cc.cc
                    openssl
                    zlib
                  ];
              in
              pkgs.mkShell {
                buildInputs = with pkgs; [
                  stdenv.cc.cc
                  openssl
                  zlib
                ];

                nativeBuildInputs = with pkgs; [
                  nil
                  nixd
                  nixfmt

                  git
                  act
                  go-task
                  husky

                  # YAML
                  yamllint
                  yamlfmt

                  # TOML
                  tombi

                  # Python
                  uv
                  ty
                  ruff
                  (python313.withPackages (
                    ps: with ps; [
                      spacy-models.en_core_web_sm
                    ]
                  ))

                  # LaTeX
                  perl
                  latex

                  texlab
                  tex-fmt
                  zathura
                ];

                shellHook = ''
                  export "LD_LIBRARY_PATH=''$LD_LIBRARY_PATH:${libraryPath}"
                  rm -rf .zed || true
                  mkdir -p .zed || true
                  cp ${__zed}/settings.json .zed/settings.json || true
                  husky install > /dev/null 2>&1 || true
                  uv sync
                '';
              };
            build =
              let
                libraryPath =
                  with pkgs;
                  lib.makeLibraryPath [
                    stdenv.cc.cc
                    openssl
                    zlib
                  ];
              in
              pkgs.mkShell {
                buildInputs = with pkgs; [
                  stdenv.cc.cc
                  openssl
                  zlib
                ];

                nativeBuildInputs = with pkgs; [
                  git
                  go-task

                  # Python
                  uv
                  ty
                  ruff
                  python313
                ];

                shellHook = ''
                  export "LD_LIBRARY_PATH=''$LD_LIBRARY_PATH:${libraryPath}"
                  uv sync &> /dev/null
                  uv run python3 -m nltk.downloader punkt_tab averaged_perceptron_tagger_eng &> /dev/null
                '';
              };
          };
        };
    };
}
