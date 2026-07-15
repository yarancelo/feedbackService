// Leveled console logger. One tiny function per concern.
const LEVELS = { debug: 10, info: 20, warn: 30, error: 40 }

let threshold = LEVELS.debug

export function setLevel(name) {
  if (name in LEVELS) threshold = LEVELS[name]
}

function emit(level, args) {
  if (LEVELS[level] < threshold) return
  const sink =
    level === 'debug' ? console.debug
    : level === 'info' ? console.info
    : level === 'warn' ? console.warn
    : console.error
  sink(`[${level.toUpperCase()}]`, ...args)
}

export const logger = {
  debug: (...args) => emit('debug', args),
  info: (...args) => emit('info', args),
  warn: (...args) => emit('warn', args),
  error: (...args) => emit('error', args),
}
