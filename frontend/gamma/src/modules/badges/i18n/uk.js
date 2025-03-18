import { defineMessages } from 'react-intl';

const messages = defineMessages({
  pageTitle: {
    id: 'modules.badges.heading.text',
    defaultMessage: 'Налаштування значків',
    description: 'Текст, що відображається у заголовку сторінки налаштування значків.',
  },
  pageDescription: {
    id: 'modules.badges.page.description',
    defaultMessage: 'Ця сторінка відображає значки та дозволяє користувачам створювати і редагувати їх.',
    description: 'Опис сторінки налаштування значків.',
  },
  addBadgeBtnText: {
    id: 'modules.badges.button.add-badge',
    defaultMessage: 'Додати значок',
    description: 'Текст, що відображається на кнопці додавання значка.',
  },
  totalBadgesCount: {
    id: 'modules.badges.total-badges.counter.text',
    defaultMessage: 'Загальна кількість значків: {badgesCount}',
    description: 'Текст, що відображається для загальної кількості значків.',
  },
  badgeEditBtnTitle: {
    id: 'modules.badges.badge-item.button.edit.title',
    defaultMessage: 'Редагувати',
    description: 'Текст, що відображається на кнопці редагування значка.',
  },
  badgeDeleteBtnTitle: {
    id: 'modules.badges.badge-item.button.delete.title',
    defaultMessage: 'Видалити',
    description: 'Текст, що відображається на кнопці видалення значка.',
  },
  badgeDefaultTitle: {
    id: 'modules.badges.badge-item.default.title',
    defaultMessage: 'Назва значка',
    description: 'Типова назва для значка.',
  },
  badgeDefaultDescription: {
    id: 'modules.badges.badge-item.default.description',
    defaultMessage: 'Опис значка',
    description: 'Типовий опис для значка.',
  },
  alertEmptyBadgesListTitle: {
    id: 'modules.badges.alert.empty-badges-list.title',
    defaultMessage: 'Немає доступних значків',
    description: 'Заголовок для сповіщення, коли немає доступних значків.',
  },
  alertEmptyBadgesListDescription: {
    id: 'modules.badges.alert.empty-badges-list.description',
    defaultMessage: 'Наразі немає жодного значка для відображення.',
    description: 'Опис для сповіщення, коли немає доступних значків.',
  },
  addManageEntityModalTitle: {
    id: 'modules.badges.modal.add-badge.title',
    defaultMessage: 'Додати новий значок',
    description: 'Заголовок модального вікна для додавання значків.',
  },
  confirmDeletionModalTitle: {
    id: 'modules.badges.alert.modal.confirm.deletion.title',
    defaultMessage: 'Підтвердження видалення',
    description: 'Заголовок модального вікна підтвердження видалення значка.',
  },
  confirmDeletionModalDescription: {
    id: 'modules.badges.alert.modal.confirm.deletion.description',
    defaultMessage: 'Ви впевнені, що хочете видалити цей значок? Цю дію неможливо скасувати.',
    description: 'Опис у модальному вікні підтвердження видалення значка.',
  },
  toastErrorTitle: {
    id: 'modules.badges.toast.error.text',
    defaultMessage: 'Сталася помилка.',
    description: 'Текст, що відображається в сповіщенні про помилку.',
  },
  badgeCreatedTitle: {
    id: 'modules.badges.alert.badge-created.title',
    defaultMessage: 'Значок успішно створено',
    description: 'Заголовок для сповіщення, коли значок успішно створено.',
  },
  badgeEditedTitle: {
    id: 'modules.badges.alert.badge-edited.title',
    defaultMessage: 'Значок успішно відредаговано',
    description: 'Заголовок для сповіщення, коли значок успішно відредаговано.',
  },
  badgeDeletedTitle: {
    id: 'modules.badges.alert.badge-deleted.title',
    defaultMessage: 'Значок успішно видалено',
    description: 'Заголовок для сповіщення, коли значок успішно видалено.',
  },
  badgeDraftStatusText: {
    id: 'modules.badges.badge.draft.status.text',
    defaultMessage: 'Чернетка',
    description: 'Текст, який відображається для статусу значка, коли він перебуває в режимі чернетки.',
  },
  badgeActiveStatusText: {
    id: 'modules.badges.badge.active.status.text',
    defaultMessage: 'Активний',
    description: 'Текст, який відображається для статусу значка, коли він активний.',
  },
});

export default messages;
