// Admin feedback list: filters, sorting, pagination, delete.
import Button from '../../components/Button.jsx'
import ErrorBanner from '../../components/ErrorBanner.jsx'
import { useFeedbackList } from '../../hooks/useFeedbackList.js'
import { formatTimestamp } from '../../lib/datetime.js'

export default function FeedbackList({ onLogout }) {
  const list = useFeedbackList({ onUnauthorized: onLogout })

  return (
    <div className="wrap">
      <div className="admin">
        <div className="topbar">
          <h1 className="topbar__title">Анонимная обратная связь</h1>
          <Button variant="ghost" onClick={onLogout}>Выйти</Button>
        </div>

        <div className="toolbar">
          <div className="toolbar__group">
            <label className="label" htmlFor="order">Сортировка</label>
            <select id="order" className="control" value={list.order}
                    onChange={(e) => { list.setOrder(e.target.value); list.setPage(1) }}>
              <option value="desc">Сначала новые</option>
              <option value="asc">Сначала старые</option>
            </select>
          </div>
          <div className="toolbar__group">
            <label className="label" htmlFor="from">От</label>
            <input id="from" className="control" type="date" value={list.dateFrom}
                   onChange={(e) => list.setDateFrom(e.target.value)} />
          </div>
          <div className="toolbar__group">
            <label className="label" htmlFor="to">До</label>
            <input id="to" className="control" type="date" value={list.dateTo}
                   onChange={(e) => list.setDateTo(e.target.value)} />
          </div>
          <div className="toolbar__spacer" />
          <Button variant="ghost" onClick={list.applyFilters}>Применить</Button>
        </div>

        <ErrorBanner message={list.error} />

        <div className="count">
          {list.loading ? 'Загружаем…' : `Всего сообщений: ${list.total}`}
        </div>

        {!list.loading && list.items.length === 0 ? (
          <div className="empty">
            <p className="empty__title">Сообщений пока нет</p>
            <p>Новые сообщения появятся здесь.</p>
          </div>
        ) : (
          list.items.map((item) => (
            <div className="item" key={item.id}>
              <div className="item__top">
                <p className="item__topic">{item.topic}</p>
                <span className="item__time">{formatTimestamp(item.created_at)}</span>
              </div>
              <p className="item__body">{item.body}</p>
              <div className="item__actions">
                <Button variant="danger" onClick={() => list.remove(item.id)}>Удалить</Button>
              </div>
            </div>
          ))
        )}

        {list.totalPages > 1 && (
          <div className="pager">
            <Button variant="ghost" disabled={list.page <= 1}
                    onClick={() => list.setPage((p) => p - 1)}>← Назад</Button>
            <span className="pager__label">{list.page} из {list.totalPages}</span>
            <Button variant="ghost" disabled={list.page >= list.totalPages}
                    onClick={() => list.setPage((p) => p + 1)}>Вперёд →</Button>
          </div>
        )}
      </div>
    </div>
  )
}
