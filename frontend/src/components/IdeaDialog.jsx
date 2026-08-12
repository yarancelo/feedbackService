import { useEffect } from 'react'

export default function IdeaDialog({ idea, onClose, onReact }) {
  useEffect(() => {
    const escape = (event) => event.key === 'Escape' && onClose()
    window.addEventListener('keydown', escape)
    return () => window.removeEventListener('keydown', escape)
  }, [onClose])
  if (!idea) return null
  return <div className="idea-dialog__backdrop" role="presentation" onMouseDown={onClose}>
    <section className="idea-dialog" role="dialog" aria-modal="true" aria-label="Идея" onMouseDown={(event) => event.stopPropagation()}>
      <button type="button" className="idea-dialog__close" aria-label="Закрыть" onClick={onClose}>×</button>
      <p className="eyebrow">{idea.status === 'accepted' ? 'Принята' : 'На рассмотрении'}</p>
      {idea.category && <span className="idea-card__category">{idea.category}</span>}
      <h2>{idea.topic || 'Без названия'}</h2>
      <p className="idea-dialog__body">{idea.body}</p>
      <footer><span>{idea.author_name ? `${idea.author_name}${idea.author_department ? ` · ${idea.author_department}` : ''}` : 'Анонимно'}</span>
        <div className="reaction-row"><button className={idea.viewer_reaction === 1 ? 'reaction is-active' : 'reaction'} onClick={() => onReact(idea, idea.viewer_reaction === 1 ? 0 : 1)}>👍 {idea.likes}</button><button className={idea.viewer_reaction === -1 ? 'reaction is-active' : 'reaction'} onClick={() => onReact(idea, idea.viewer_reaction === -1 ? 0 : -1)}>👎 {idea.dislikes}</button></div>
      </footer>
    </section>
  </div>
}
