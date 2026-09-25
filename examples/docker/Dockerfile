# ---------------------------------------------------------------------------
# Hardened container image — the "after" for lab 2.2 and project P2.
#
# Compare with Dockerfile.naive in this directory. Almost all of the CVE
# reduction between the two comes from one decision — the runtime base image —
# and almost none of it comes from the application's own dependencies. That is
# the single most useful thing to internalise about container scanning.
#
#   docker build -t app:hardened .
#   docker run --rm --read-only --cap-drop=ALL --security-opt=no-new-privileges app:hardened
#   trivy image --config ../trivy/trivy.yaml app:hardened
#
# Digests below were current when this was written. Resolve your own and let
# Renovate keep them fresh (see ../renovate/renovate.json):
#   docker buildx imagetools inspect node:22-bookworm-slim
# ---------------------------------------------------------------------------

# syntax=docker/dockerfile:1

# --- Stage 1: dependencies -------------------------------------------------
# A full-fat base is fine here. Nothing from this stage reaches production
# except the files we explicitly copy forward, so its CVEs are not shipped.
FROM node:22-bookworm-slim@sha256:d649c27dae7ba0137b3cef5dd75baa422c08dc3d9e3fc0c23dfb172dc3cc6436 AS deps

WORKDIR /app

# Copy manifests only, so this layer caches until dependencies actually change.
COPY package.json package-lock.json ./

# `npm ci` installs exactly what the lockfile says, with integrity hashes —
# `npm install` may silently resolve something else. --ignore-scripts stops a
# compromised transitive dependency executing at install time, which is how a
# large share of npm supply chain attacks actually land. Drop the flag only
# for packages that genuinely need it, and know which ones they are.
RUN --mount=type=cache,target=/root/.npm \
    npm ci --omit=dev --ignore-scripts

# --- Stage 2: build --------------------------------------------------------
FROM node:22-bookworm-slim@sha256:d649c27dae7ba0137b3cef5dd75baa422c08dc3d9e3fc0c23dfb172dc3cc6436 AS build

WORKDIR /app

COPY package.json package-lock.json ./
RUN --mount=type=cache,target=/root/.npm \
    npm ci --ignore-scripts

COPY . .

# Build-time secrets go through BuildKit mounts, never through ARG or ENV —
# both are recoverable from image history by anyone who can pull the image.
#   docker build --secret id=npmrc,src=$HOME/.npmrc .
# RUN --mount=type=secret,id=npmrc,target=/root/.npmrc npm run build
RUN npm run build && npm prune --omit=dev

# --- Stage 3: runtime ------------------------------------------------------
# Distroless: no shell, no package manager, no coreutils. An attacker with RCE
# lands in an environment with nothing to pivot with — no curl to pull a stage
# two, no sh to run it. It also removes hundreds of CVEs you were never going
# to fix, because the packages carrying them are simply not present.
#
# The `nonroot` tag runs as UID 65532 by default.
#
# Wolfi/Chainguard images are the other strong option and are usually patched
# faster than distroless, which inherits Debian stable's release cadence. Pick
# one, know why, and pin it by digest either way.
FROM gcr.io/distroless/nodejs22-debian12:nonroot@sha256:13593b7570658e8477de39e2f4a1dd25db2f836d68a0ba771251572d23bb4f8e AS runtime

# OCI labels: how a scanner, a registry, and an incident responder at 2am work
# out what this image is and where it came from.
LABEL org.opencontainers.image.title="example-service" \
      org.opencontainers.image.source="https://github.com/siddhantbhattarai/DevSecOps-Roadmap" \
      org.opencontainers.image.licenses="Apache-2.0" \
      org.opencontainers.image.base.name="gcr.io/distroless/nodejs22-debian12:nonroot"

WORKDIR /app

# Copy only what runs. Not the toolchain, not the tests, not the .git
# directory, not the CI config — see .dockerignore.
# --chown is set explicitly so the files are not owned by the running user;
# an application that cannot overwrite its own code is one that cannot be
# persistently backdoored through a file write bug.
COPY --from=deps  --chown=root:root /app/node_modules ./node_modules
COPY --from=build --chown=root:root /app/dist         ./dist
COPY --from=build --chown=root:root /app/package.json ./package.json

ENV NODE_ENV=production \
    NODE_OPTIONS="--max-old-space-size=512"

# Explicit and numeric. `USER nonroot` depends on a passwd entry existing;
# a UID always works, and Kubernetes `runAsNonRoot` can verify it without
# resolving a name.
USER 65532:65532

EXPOSE 3000

# Distroless nodejs images use node as the entrypoint, so no shell is
# involved — exec form only. Shell form would need a shell that is not here.
CMD ["dist/server.js"]

# ---------------------------------------------------------------------------
# What this Dockerfile cannot do for you
#
# The runtime flags are not in the image, and they matter as much as anything
# above. Enforce them where the workload runs:
#
#   docker: --read-only --cap-drop=ALL --security-opt=no-new-privileges
#           --tmpfs /tmp:rw,noexec,nosuid --pids-limit --memory --cpus
#
#   Kubernetes securityContext:
#     runAsNonRoot: true
#     runAsUser: 65532
#     allowPrivilegeEscalation: false
#     readOnlyRootFilesystem: true
#     capabilities: { drop: ["ALL"] }
#     seccompProfile: { type: RuntimeDefault }
#
#   ...and enforce that with admission control, not with review:
#   see ../kyverno/baseline-policies.yaml
#
# Then sign it and verify the signature at admission, or none of the above
# tells you that what is running is what you built:
#   see ../github-actions/devsecops-pipeline.yml
# ---------------------------------------------------------------------------
