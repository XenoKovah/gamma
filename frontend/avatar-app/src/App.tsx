import React, { useEffect, useRef } from 'react';
import { useMascotStore } from "./state/mascot.state";
import { useDrawCanvasHook } from "./hooks/useDrawCanvasHook";
import clsx from "clsx";
import { IMascotColors } from "./interfaces/interfaces";
import MascotItems from "./components/MascotItems";
import Slider from "react-slick";
import "slick-carousel/slick/slick.css";
import MascotColor from "./components/Color";

function App() {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  const {
    isLoading,
    colors,
    glasses,
    headdress,
    emotion: emotions,
    outerwear,
    selectedMascotData,
    setSelectedMascotData,
    canvasImgUrl,
    isMascotUpdating,
    updateMascot,
    createMascot,
  } = useMascotStore();

  useDrawCanvasHook({
    canvasRef,
    color: selectedMascotData?.colors?.hex_color || '#00F4AE',
  });

  const handleDownload = () => {
    if (!canvasImgUrl) {
      return;
    }

    const image = canvasImgUrl.replace("image/png", "image/octet-stream");
    const link = document.createElement('a');
    link.download = 'mascot.png';
    link.href = image;
    link.click();
  };

  const handleSubmit = async () => {
    if (isLoading) {
      return;
    }

    if (isMascotUpdating) {
      await updateMascot();
    } else {
      await createMascot();

      window.location.assign(process.env.REACT_APP_REDIRECT_AFTER_MASCOT_CREATION || '')
    }
  };

  const handleColorSelection = (value: IMascotColors) => {
    if (isLoading) {
      return;
    }

    setSelectedMascotData({
      colors: value,
    });
  };

  const settings = {
    arrows: true,
    dots: false,
    infinite: true,
    variableWidth: true,
    slidesToShow: 1,
    slidesToScroll: 1,
  };

  return (
    <div className="mascot-holder">
      <div className="mascot-hero-holder">

        <div className="mascot-hero-image">
          <canvas ref={canvasRef} style={{ display: 'none' }}/>

          <img src={canvasImgUrl} alt="mascot_sample_big"/>

          <div className="mascot-switcher-holder">
            <label className="switch">
              <input type="checkbox" defaultChecked={selectedMascotData?.use_mascot} onChange={() => {
                setSelectedMascotData({
                  use_mascot: !selectedMascotData?.use_mascot,
                });
              }} checked={selectedMascotData?.use_mascot}/>
              <span className="switch-toggle"></span>
            </label>
            Застосувати на аватарі
          </div>
        </div>
        <Slider {...settings} className="mascot-hero-color-picker">
          {!!colors.length && colors.map((item) => {
              return (
                <>
                  <div
                    onClick={() => handleColorSelection(item)}
                    className={clsx('mascot-hero-color-item', {
                      ['is-active']: selectedMascotData?.colors?.hex_color.toLowerCase() === item.hex_color.toLowerCase()
                    })}
                    key={'color_' + item.id}
                  >
                    <MascotColor color={item.hex_color}/>
                  </div>
                </>
              );
            }
          )}
        </Slider>
        <div className={"btn-holder"}>
          <button type="button" disabled={isLoading} className={"btn-outlined btn-large"} onClick={handleDownload}>
            <svg className="icon-svg">
              <use xlinkHref={'/static/avatar-app/images/svg-sprite.svg#ico-download-square'}/>
            </svg>
            Завантажити
          </button>
          <button type="button" disabled={isLoading} className="btn-outlined btn-large">
            <svg className="icon-svg">
              <use xlinkHref={'/static/avatar-app/images/svg-sprite.svg#ico-share-square'}/>
            </svg>
            Поділитись
          </button>

          <button type="button" disabled={isLoading} className={"btn-primary btn-large"} onClick={handleSubmit}>
            {isMascotUpdating ? 'Зберегти' : 'Створити маскот'}
          </button>
        </div>
      </div>
      <div className="mascot-wardrobe-holder">
        <div className="mascot-tabs-container">
          <ul className="mascot-tabs-switcher-list">
            <li className="mascot-tabs-switcher-list-item is-active" data-tab="mascot-tab1">
              <span className="wardrobe-new-update"></span>
              Окуляри
            </li>
            <li className="mascot-tabs-switcher-list-item" data-tab="mascot-tab2">
              <span className="wardrobe-new-update"></span>
              Головний убір
            </li>
            <li className="mascot-tabs-switcher-list-item" data-tab="mascot-tab3">
              <span className="wardrobe-new-update"></span>
              Верхній одяг
            </li>
            <li className="mascot-tabs-switcher-list-item" data-tab="mascot-tab4">
              <span className="wardrobe-new-update"></span>
              Емоції
            </li>
          </ul>
          <div className="mascot-tabs-content-holder" role="tablist">
            <div className="mascot-tabs-content-item" role="tab" id="mascot-tab1">
              <ul className="mascot-wardrobe-list">
                <MascotItems
                  items={glasses || []}
                  dataKey={'glasses'}
                  selectedItem={selectedMascotData?.glasses}
                />
              </ul>
            </div>
            <div className="mascot-tabs-content-item" role="tab" id="mascot-tab2">
              <ul className="mascot-wardrobe-list">
                <MascotItems
                  items={headdress || []}
                  dataKey={'headdress'}
                  selectedItem={selectedMascotData?.headdress}
                />
              </ul>
            </div>
            <div className="mascot-tabs-content-item" role="tab" id="mascot-tab3">
              <ul className="mascot-wardrobe-list">
                <MascotItems
                  items={outerwear || []}
                  dataKey={'outerwear'}
                  selectedItem={selectedMascotData?.outerwear}
                />
              </ul>
            </div>
            <div className="mascot-tabs-content-item" role="tab" id="mascot-tab4">
              <ul className="mascot-wardrobe-list">
                <MascotItems
                  items={emotions || []}
                  dataKey={'emotion'}
                  selectedItem={selectedMascotData?.emotion}
                />
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
