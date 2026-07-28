import { useEffect, useMemo, useRef } from "react";
import type {
  ComparisonCase,
  FeatureImportance,
  Horizon,
  Language,
  Modality,
  TestCase,
} from "../types";
import { MODALITY_COLORS, normalizeModality } from "../utils";

const FONT = '"Segoe UI", system-ui, sans-serif';
const INK = "#f3f0e7";
const MUTED = "#8fa89f";
const GRID = "rgba(243, 240, 231, 0.1)";

interface CanvasSize {
  width: number;
  height: number;
  ratio: number;
}

function setupCanvas(canvas: HTMLCanvasElement): CanvasSize {
  const ratio = Math.min(window.devicePixelRatio || 1, 2);
  const width = Math.max(1, canvas.clientWidth);
  const height = Math.max(1, canvas.clientHeight);
  if (canvas.width !== Math.round(width * ratio) || canvas.height !== Math.round(height * ratio)) {
    canvas.width = Math.round(width * ratio);
    canvas.height = Math.round(height * ratio);
  }
  const context = canvas.getContext("2d");
  context?.setTransform(ratio, 0, 0, ratio, 0, 0);
  return { width, height, ratio };
}

function observeCanvas(canvas: HTMLCanvasElement, draw: () => void): () => void {
  const Observer = globalThis.ResizeObserver;
  if (typeof Observer !== "undefined") {
    const observer = new Observer(draw);
    observer.observe(canvas);
    return () => observer.disconnect();
  }
  globalThis.addEventListener("resize", draw);
  return () => globalThis.removeEventListener("resize", draw);
}

interface SignalLoomProps {
  counts: Record<Modality, number>;
  horizon: Horizon;
  language: Language;
  paused: boolean;
  labels: Record<Modality, string>;
}

export function SignalLoom({
  counts,
  horizon,
  language,
  paused,
  labels,
}: SignalLoomProps) {
  const ref = useRef<HTMLCanvasElement>(null);
  const animationRef = useRef<number | null>(null);
  const previousRef = useRef<Record<Modality, number>>(counts);
  const startedRef = useRef(performance.now());

  const active = useMemo(
    () =>
      (Object.entries(counts) as [Modality, number][])
        .filter(([, count]) => count > 0)
        .sort(([a], [b]) => {
          const order: Modality[] = [
            "soil",
            "sentinel1",
            "sentinel2",
            "weather",
            "context",
            "other",
          ];
          return order.indexOf(a) - order.indexOf(b);
        }),
    [counts],
  );

  useEffect(() => {
    const canvas = ref.current;
    if (!canvas) return;
    const context = canvas.getContext("2d");
    if (!context) return;
    const start = performance.now();
    const from = previousRef.current;
    previousRef.current = counts;

    const draw = (now = performance.now()) => {
      const { width, height } = setupCanvas(canvas);
      context.clearRect(0, 0, width, height);
      const centerX = width * 0.58;
      const centerY = height * 0.5;
      const elapsed = (now - startedRef.current) / 1000;
      const morph = Math.min(1, (now - start) / 650);
      const eased = 1 - Math.pow(1 - morph, 3);

      const glow = context.createRadialGradient(
        centerX,
        centerY,
        0,
        centerX,
        centerY,
        Math.min(width, height) * 0.33,
      );
      glow.addColorStop(0, "rgba(218, 242, 163, 0.12)");
      glow.addColorStop(1, "rgba(218, 242, 163, 0)");
      context.fillStyle = glow;
      context.fillRect(0, 0, width, height);

      active.forEach(([modality, targetCount], groupIndex) => {
        const oldCount = from[modality] ?? targetCount;
        const animatedCount = oldCount + (targetCount - oldCount) * eased;
        const yBase = ((groupIndex + 1) / (active.length + 1)) * height;
        const color = MODALITY_COLORS[modality];
        const lineCount = Math.max(1, Math.round(animatedCount));
        const beamHeight = Math.min(height / (active.length + 1) - 10, 56);

        for (let index = 0; index < lineCount; index += 1) {
          const fraction = lineCount === 1 ? 0.5 : index / (lineCount - 1);
          const y = yBase + (fraction - 0.5) * beamHeight;
          const wobble = paused ? 0 : Math.sin(elapsed * 1.25 + index * 0.73) * 2.4;
          context.beginPath();
          context.moveTo(0, y + wobble);
          context.bezierCurveTo(
            width * 0.22,
            y + wobble,
            centerX - width * 0.15,
            centerY + (y - centerY) * 0.24,
            centerX,
            centerY,
          );
          context.strokeStyle = color;
          context.globalAlpha = 0.2 + (index % 4) * 0.06;
          context.lineWidth = 0.7;
          context.stroke();
        }

        context.globalAlpha = 1;
        context.fillStyle = color;
        context.font = `600 11px ${FONT}`;
        context.textAlign = "left";
        context.fillText(
          `${labels[modality]} · ${targetCount}`,
          16,
          Math.max(14, yBase - beamHeight / 2 - 8),
        );
      });

      context.globalAlpha = 1;
      context.beginPath();
      context.arc(centerX, centerY, 29, 0, Math.PI * 2);
      context.fillStyle = "#dff6a5";
      context.shadowColor = "rgba(223, 246, 165, 0.7)";
      context.shadowBlur = 28;
      context.fill();
      context.shadowBlur = 0;
      context.fillStyle = "#071a16";
      context.font = `700 9px ${FONT}`;
      context.textAlign = "center";
      context.fillText("MODEL", centerX, centerY + 3);

      const timelineStart = centerX + 30;
      const timelineEnd = width - 20;
      context.beginPath();
      context.moveTo(timelineStart, centerY);
      context.bezierCurveTo(
        width * 0.72,
        centerY - height * 0.13,
        width * 0.84,
        centerY + height * 0.12,
        timelineEnd,
        centerY,
      );
      context.strokeStyle = "#dff6a5";
      context.lineWidth = 2;
      context.globalAlpha = 0.85;
      context.stroke();

      for (let index = 0; index < 6; index += 1) {
        const progress = ((paused ? 0.45 : elapsed * 0.08) + index / 6) % 1;
        const x = timelineStart + (timelineEnd - timelineStart) * progress;
        const wave = Math.sin(progress * Math.PI * 2) * height * 0.055;
        context.beginPath();
        context.arc(x, centerY + wave, 2.2, 0, Math.PI * 2);
        context.fillStyle = "#f3f0e7";
        context.globalAlpha = 0.35 + progress * 0.6;
        context.fill();
      }

      context.globalAlpha = 1;
      context.fillStyle = MUTED;
      context.textAlign = "right";
      context.font = `500 10px ${FONT}`;
      context.fillText(horizon === "may31" ? "31 MAY" : "15 JUN", width - 18, centerY - 14);

      if (!paused && morph < 1) animationRef.current = requestAnimationFrame(draw);
      else if (!paused) animationRef.current = requestAnimationFrame(draw);
    };

    draw();
    const stopObserve = observeCanvas(canvas, () => draw());
    return () => {
      stopObserve();
      if (animationRef.current !== null) cancelAnimationFrame(animationRef.current);
    };
  }, [active, counts, horizon, labels, paused]);

  const description = active
    .map(([modality, count]) => `${labels[modality]}: ${count}`)
    .join(", ");

  return (
    <figure className="canvas-figure loom-figure">
      <canvas
        ref={ref}
        className="loom-canvas"
        role="img"
        aria-label={`${language === "fr" ? "Tissage des modalités" : "Modality signal loom"}. ${description}`}
      />
      <figcaption className="sr-only">{description}</figcaption>
    </figure>
  );
}

interface TruthLensProps {
  cases: TestCase[];
  language: Language;
}

export function TruthLens({ cases, language }: TruthLensProps) {
  const ref = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = ref.current;
    if (!canvas) return;
    const draw = () => {
      const context = canvas.getContext("2d");
      if (!context) return;
      const { width, height } = setupCanvas(canvas);
      context.clearRect(0, 0, width, height);
      const padding = Math.max(34, Math.min(width, height) * 0.12);
      const values = cases.flatMap((item) => [item.actual_doy, item.predicted_doy]);
      if (!values.length) return;
      const min = Math.floor(Math.min(...values) - 2);
      const max = Math.ceil(Math.max(...values) + 2);
      const range = Math.max(1, max - min);
      const x = (value: number) => padding + ((value - min) / range) * (width - padding * 2);
      const y = (value: number) => height - padding - ((value - min) / range) * (height - padding * 2);

      context.strokeStyle = GRID;
      context.lineWidth = 1;
      for (let index = 0; index <= 4; index += 1) {
        const fraction = index / 4;
        const gridX = padding + fraction * (width - padding * 2);
        const gridY = padding + fraction * (height - padding * 2);
        context.beginPath();
        context.moveTo(gridX, padding);
        context.lineTo(gridX, height - padding);
        context.stroke();
        context.beginPath();
        context.moveTo(padding, gridY);
        context.lineTo(width - padding, gridY);
        context.stroke();
      }

      context.beginPath();
      context.moveTo(x(min), y(min));
      context.lineTo(x(max), y(max));
      context.strokeStyle = "rgba(223, 246, 165, .65)";
      context.setLineDash([5, 7]);
      context.stroke();
      context.setLineDash([]);

      for (const item of cases) {
        context.beginPath();
        context.arc(x(item.actual_doy), y(item.predicted_doy), 2.8, 0, Math.PI * 2);
        context.fillStyle =
          item.predicted_doy >= item.actual_doy
            ? "rgba(104, 184, 255, .62)"
            : "rgba(242, 212, 111, .62)";
        context.fill();
      }

      context.fillStyle = MUTED;
      context.font = `500 10px ${FONT}`;
      context.textAlign = "center";
      context.fillText(
        language === "fr" ? "Jour réel" : "Actual day",
        width / 2,
        height - 8,
      );
      context.save();
      context.translate(12, height / 2);
      context.rotate(-Math.PI / 2);
      context.fillText(language === "fr" ? "Jour prédit" : "Predicted day", 0, 0);
      context.restore();
    };
    draw();
    return observeCanvas(canvas, draw);
  }, [cases, language]);

  return (
    <canvas
      ref={ref}
      className="proof-canvas"
      role="img"
      aria-label={
        language === "fr"
          ? `Nuage de ${cases.length} prévisions comparées aux valeurs réelles`
          : `Scatter plot of ${cases.length} predictions against actual values`
      }
    />
  );
}

interface ComparisonPlotProps {
  cases: ComparisonCase[];
  language: Language;
}

export function ComparisonPlot({ cases, language }: ComparisonPlotProps) {
  const ref = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = ref.current;
    if (!canvas) return;
    const draw = () => {
      const context = canvas.getContext("2d");
      if (!context) return;
      const { width, height } = setupCanvas(canvas);
      context.clearRect(0, 0, width, height);
      if (!cases.length) return;
      const padding = Math.max(34, Math.min(width, height) * 0.13);
      const maxError = Math.max(
        1,
        ...cases.flatMap((item) => [
          item.may31_absolute_error_days ?? item.absolute_error_may31 ?? 0,
          item.june15_absolute_error_days ?? item.absolute_error_june15 ?? 0,
        ]),
      );
      const x = (value: number) => padding + (value / maxError) * (width - padding * 2);
      const y = (value: number) =>
        height - padding - (value / maxError) * (height - padding * 2);

      context.beginPath();
      context.moveTo(x(0), y(0));
      context.lineTo(x(maxError), y(maxError));
      context.strokeStyle = "rgba(243, 240, 231, .25)";
      context.setLineDash([4, 6]);
      context.stroke();
      context.setLineDash([]);

      for (const item of cases) {
        const may = item.may31_absolute_error_days ?? item.absolute_error_may31 ?? 0;
        const june = item.june15_absolute_error_days ?? item.absolute_error_june15 ?? 0;
        const better = june < may;
        context.beginPath();
        context.arc(
          x(may),
          y(june),
          2.7,
          0,
          Math.PI * 2,
        );
        context.fillStyle = better
          ? "rgba(143, 219, 128, .7)"
          : "rgba(242, 212, 111, .58)";
        context.fill();
      }

      context.fillStyle = MUTED;
      context.font = `500 10px ${FONT}`;
      context.textAlign = "center";
      context.fillText(
        language === "fr" ? "Erreur au 31 mai" : "May 31 error",
        width / 2,
        height - 8,
      );
      context.save();
      context.translate(12, height / 2);
      context.rotate(-Math.PI / 2);
      context.fillText(
        language === "fr" ? "Erreur au 15 juin" : "June 15 error",
        0,
        0,
      );
      context.restore();
    };
    draw();
    return observeCanvas(canvas, draw);
  }, [cases, language]);

  return (
    <canvas
      ref={ref}
      className="duel-canvas"
      role="img"
      aria-label={
        language === "fr"
          ? `Comparaison des erreurs de ${cases.length} cas appariés`
          : `Error comparison for ${cases.length} paired cases`
      }
    />
  );
}

interface ConstellationProps {
  features: FeatureImportance[];
  language: Language;
}

export function Constellation({ features, language }: ConstellationProps) {
  const ref = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = ref.current;
    if (!canvas) return;
    const draw = () => {
      const context = canvas.getContext("2d");
      if (!context) return;
      const { width, height } = setupCanvas(canvas);
      context.clearRect(0, 0, width, height);
      const items = [...features]
        .filter((item) => Number.isFinite(item.importance_mean))
        .sort((a, b) => b.importance_mean - a.importance_mean)
        .slice(0, 18);
      if (!items.length) return;
      const centerX = width / 2;
      const centerY = height / 2;
      const max = Math.max(...items.map((item) => Math.abs(item.importance_mean)), 0.001);
      const orbit = Math.min(width, height) * 0.36;

      items.forEach((item, index) => {
        const angle = index * 2.399963 + 0.25;
        const radial = orbit * (0.3 + 0.7 * Math.sqrt((index + 1) / items.length));
        const x = centerX + Math.cos(angle) * radial * (width > height ? 1.35 : 0.9);
        const y = centerY + Math.sin(angle) * radial;
        const normalized = Math.max(0, item.importance_mean) / max;
        const radius = 3.5 + Math.sqrt(normalized) * 10;
        const modality = normalizeModality(item.modality, item.feature);
        const color = MODALITY_COLORS[modality];

        context.beginPath();
        context.moveTo(centerX, centerY);
        context.lineTo(x, y);
        context.strokeStyle = `${color}28`;
        context.lineWidth = 0.7;
        context.stroke();

        const halo = context.createRadialGradient(x, y, 0, x, y, radius * 2.8);
        halo.addColorStop(0, `${color}aa`);
        halo.addColorStop(0.38, `${color}48`);
        halo.addColorStop(1, `${color}00`);
        context.beginPath();
        context.arc(x, y, radius * 2.8, 0, Math.PI * 2);
        context.fillStyle = halo;
        context.fill();

        context.beginPath();
        context.arc(x, y, radius, 0, Math.PI * 2);
        context.fillStyle = color;
        context.globalAlpha = 0.85;
        context.fill();
        context.globalAlpha = 1;
      });

      context.beginPath();
      context.arc(centerX, centerY, 4, 0, Math.PI * 2);
      context.fillStyle = INK;
      context.fill();
    };
    draw();
    return observeCanvas(canvas, draw);
  }, [features]);

  return (
    <canvas
      ref={ref}
      className="proof-canvas"
      role="img"
      aria-label={
        language === "fr"
          ? `Constellation de ${features.length} importances globales`
          : `Constellation of ${features.length} global feature importances`
      }
    />
  );
}
