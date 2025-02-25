import { defineMessages } from 'react-intl';

const messages = defineMessages({
  pageTitle: {
    id: 'modules.avatars.heading.text',
    defaultMessage: 'Налаштування аватарів',
    description: 'Текст, що відображається в заголовку сторінки налаштувань аватарів.',
  },
  pageDescription: {
    id: 'modules.avatars.page.description',
    defaultMessage: 'Ця сторінка відображає аватари та дозволяє користувачам створювати і редагувати їх.',
    description: 'Опис сторінки налаштувань аватарів.',
  },
  totalAvatarSetsCount: {
    id: 'modules.avatars.total-avatars.counter.text',
    defaultMessage: 'Загальна кількість аватарів: {avatarSetsCount}',
    description: 'Текст, що відображає загальну кількість аватарів.',
  },
  addAvatarBtnText: {
    id: 'modules.avatars.button.add-avatar',
    defaultMessage: 'Додати аватар',
    description: 'Текст, що відображається на кнопці додавання аватара.',
  },
  alertEmptyAvatarsListTitle: {
    id: 'modules.avatars.alert.empty-avatars-list.title',
    defaultMessage: 'Немає доступних аватарів',
    description: 'Заголовок сповіщення, коли немає аватарів для відображення.',
  },
  alertEmptyAvatarsListDescription: {
    id: 'modules.avatars.alert.empty-avatars-list.description',
    defaultMessage: 'Наразі немає аватарів для відображення.',
    description: 'Опис сповіщення, коли немає аватарів для відображення.',
  },
  avatarEditBtnTitle: {
    id: 'modules.avatars.avatar-item.button.edit.title',
    defaultMessage: 'Редагувати',
    description: 'Текст, що відображається на кнопці редагування аватара.',
  },
  avatarDeleteBtnTitle: {
    id: 'modules.avatars.avatar-item.button.delete.title',
    defaultMessage: 'Видалити',
    description: 'Текст, що відображається на кнопці видалення аватара.',
  },
  toastErrorTitle: {
    id: 'modules.avatars.toast.error.text',
    defaultMessage: 'Сталася помилка.',
    description: 'Текст, що відображається в сповіщенні про помилку.',
  },
  confirmDeletionModalTitle: {
    id: 'modules.avatars.alert.modal.confirm.deletion.title',
    defaultMessage: 'Підтвердження видалення',
    description: 'Заголовок модального вікна підтвердження видалення аватар сету.',
  },
  confirmDeletionModalDescription: {
    id: 'modules.avatars.alert.modal.confirm.deletion.description',
    defaultMessage: 'Ви впевнені, що хочете видалити цей аватар сет? Цю дію неможливо скасувати.',
    description: 'Опис у модальному вікні підтвердження видалення аватар сету.',
  },
});

export default messages;
