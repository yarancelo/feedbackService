import { useEffect, useRef, useState } from 'react'
import { createComment, listComments } from '../api/comments.js'

export default function IdeaDialog({ idea, onClose, onReact }) {
  const [comments, setComments] = useState([])
  const [comment, setComment] = useState('')
  const [error, setError] = useState('')
  const [sending, setSending] = useState(false)
  const closeRef = useRef(null)
  useEffect(() => { const escape = (event) => event.key === 'Escape' && onClose(); window.addEventListener('keydown', escape); return () => window.removeEventListener('keydown', escape) }, [onClose])
  useEffect(() => { if (!idea) return; setComment(''); setError(''); listComments(idea.id).then(setComments).catch((requestError) => setError(requestError.message)) }, [idea?.id])
  useEffect(() => { if (!idea) return; closeRef.current?.focus(); const previous = document.body.style.overflow; document.body.style.overflow = 'hidden'; return () => { document.body.style.overflow = previous } }, [idea])
  if (!idea) return null
  async function submit(event) { event.preventDefault(); if (!comment.trim() || sending) return; setSending(true); setError(''); try { const created = await createComment(idea.id, comment.trim()); setComments((current) => [...current, created]); setComment('') } catch (requestError) { setError(requestError.message) } finally { setSending(false) } }
  return <div className="idea-dialog__backdrop" role="presentation" onMouseDown={onClose}><section className="idea-dialog" role="dialog" aria-modal="true" aria-label="Полный текст идеи" onMouseDown={(event) => event.stopPropagation()}><button ref={closeRef} type="button" className="idea-dialog__close" aria-label="Закрыть" title="Закрыть" onClick={onClose}>×</button>{idea.category && <span className="idea-card__category">{idea.category}</span>}<span className="status">Принята</span><h2>{idea.topic || 'Без названия'}</h2><p className="idea-dialog__body">{idea.body}</p><footer><span>{idea.author_name ? `${idea.author_name}${idea.author_department ? `, ${idea.author_department}` : ''}` : 'Анонимно'}</span><span>{new Date(idea.created_at).toLocaleDateString('ru-RU')}</span></footer><section className="comments"><h3>Комментарии <span>{comments.length}</span></h3>{error && <p className="comments__error" role="alert">{error}</p>}<div className="comments__list">{comments.length ? comments.map((item) => <article className="comment" key={item.id}><strong>Анонимно</strong><p>{item.body}</p></article>) : <p className="hint">Пока нет комментариев.</p>}</div><form className="comments__form" onSubmit={submit}><label className="label" htmlFor="idea-comment">Комментарий</label><textarea id="idea-comment" className="textarea" value={comment} onChange={(event) => setComment(event.target.value)} placeholder="Напишите комментарий" maxLength="2000" /><button type="submit" className="btn btn--primary" disabled={!comment.trim() || sending}>{sending ? 'Отправляем…' : 'Отправить комментарий'}</button></form></section></section></div>
}
