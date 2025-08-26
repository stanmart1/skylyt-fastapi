interface TrendingDestinationCardProps {
  state: {
    id: number;
    name: string;
    slug: string;
    featured_image_url?: string;
    hotel_count: number;
    popularity_score: number;
  };
  onClick: (slug: string) => void;
}

const TrendingDestinationCard = ({ state, onClick }: TrendingDestinationCardProps) => {
  const getCountryFlag = (stateName: string) => {
    return '🇳🇬'; // Nigeria flag for all states
  };

  return (
    <div 
      className="relative h-64 rounded-xl overflow-hidden cursor-pointer group shadow-lg hover:shadow-2xl transition-all duration-300 hover:scale-105"
      onClick={() => onClick(state.slug)}
    >
      {/* Background Image */}
      <img
        src={state.featured_image_url}
        alt={state.name}
        className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-500"
      />
      
      {/* Gradient Overlay */}
      <div className="absolute inset-0 bg-gradient-to-b from-black/50 via-transparent to-black/30" />
      
      {/* Title with Flag */}
      <div className="absolute top-4 left-4">
        <div className="flex items-center gap-2">
          <h3 className="text-xl font-bold text-white">{state.name}</h3>
          <span className="text-lg">{getCountryFlag(state.name)}</span>
        </div>
      </div>
      
      {/* Glow Border for Popular States */}
      {state.popularity_score > 8 && (
        <div className="absolute inset-0 rounded-xl border-2 border-orange-400 shadow-lg shadow-orange-400/50" />
      )}
    </div>
  );
};

export default TrendingDestinationCard;