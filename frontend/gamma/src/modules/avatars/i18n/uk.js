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
  totalAvatarsCount: {
    id: 'modules.avatars.total-avatars.counter.text',
    defaultMessage: 'Загальна кількість аватарів: {avatarsCount}',
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
    id: 'modules.avatar.avatar-item.button.delete.title',
    defaultMessage: 'Видалити',
    description: 'Текст, що відображається на кнопці видалення аватара.',
  },
});

export default messages;
