// src/components/NavigationBar.tsx
import React, { useState, memo, useCallback, useEffect, useRef } from 'react';
import { NavLink } from 'react-router-dom';
import { IoSearch } from 'react-icons/io5';
import { Divide as Hamburger } from 'hamburger-react';
import DropdownMenu from './DropdownMenu';

// NavLink의 active 상태에 따라 클래스명을 반환하는 함수
const getNavLinkClass = ({ isActive }: { isActive: boolean }) => 
  isActive ? 'text-gray-700' : 'text-white';

const NavigationBar: React.FC = memo(() => {
  const [isOpen, setIsOpen] = useState(false);
  const menuRef = useRef<HTMLLIElement>(null);

  // 메뉴를 닫는 함수
  const handleCloseMenu = useCallback(() => {
    setIsOpen(false);
  }, []);

  // 외부 클릭으로 메뉴를 닫는 효과
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        handleCloseMenu();
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [handleCloseMenu]);

  return (
    <nav className="fixed top-0 left-0 right-0 bg-white text-gray-800 p-1 flex justify-between items-center z-10 h-[56px]"> {/* [J]0602 디바이스 스타일 최적화를 위한 고정 높이값 부여 */}
      <div className="flex items-center">
        <span className="font-bold text-xl p-2 mr-3 h-[3rem]">EVTrend</span>
      </div>
      <ul className="flex items-center">
        <li className="mr-4">
          <NavLink to="/search" className={getNavLinkClass} title="Search">
            <IoSearch className="text-gray-700 text-2xl" aria-label="Search" />
          </NavLink>
        </li>
        <li className="relative" ref={menuRef}>
          <Hamburger
            toggled={isOpen}
            toggle={setIsOpen}
            color="#4B5563"
            size={24}
            aria-label="Toggle Menu"
          />
          <DropdownMenu isOpen={isOpen} onClose={handleCloseMenu} />
        </li>
      </ul>
    </nav>
  );
});

export default NavigationBar;
